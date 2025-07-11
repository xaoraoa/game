import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
import httpx
from dotenv import load_dotenv
import json
import uuid
from datetime import datetime

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(MONGO_URL)
db = client.irys_reflex
scores_collection = db.scores

class ScoreSubmission(BaseModel):
    player: str
    time: int
    penalty: bool = False
    timestamp: str
    tx_id: Optional[str] = None

class LeaderboardEntry(BaseModel):
    id: str
    player: str
    time: int
    penalty: bool
    timestamp: str
    tx_id: Optional[str] = None
    verified: bool = False

@app.on_event("startup")
async def startup_event():
    # Create indexes for efficient queries
    await scores_collection.create_index([("time", 1)])  # Ascending for best times
    await scores_collection.create_index([("player", 1)])
    # Create unique index only for non-null tx_id values
    await scores_collection.create_index([("tx_id", 1)], unique=True, sparse=True, partialFilterExpression={"tx_id": {"$ne": None}})

@app.post("/api/scores")
async def submit_score(score: ScoreSubmission):
    try:
        # Generate unique ID
        score_id = str(uuid.uuid4())
        
        # Create score document
        score_doc = {
            "id": score_id,
            "player": score.player,
            "time": score.time,
            "penalty": score.penalty,
            "timestamp": score.timestamp,
            "tx_id": score.tx_id,
            "verified": False,
            "created_at": datetime.utcnow()
        }
        
        # If there's a transaction ID, verify it
        if score.tx_id:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"https://devnet.irys.xyz/{score.tx_id}")
                    if response.status_code == 200:
                        # Try to parse the response as JSON
                        try:
                            irys_data = response.json()
                            score_doc["verified"] = True
                        except:
                            # If it's not JSON, it might be raw text
                            score_doc["verified"] = True
                    else:
                        score_doc["verified"] = False
            except:
                score_doc["verified"] = False
        
        # Insert the score
        result = await scores_collection.insert_one(score_doc)
        
        if result.inserted_id:
            return {
                "status": "success", 
                "id": score_id,
                "verified": score_doc["verified"]
            }
        
        raise HTTPException(status_code=500, detail="Failed to store score")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(limit: int = 10):
    try:
        # Get top scores (lowest reaction times are best)
        cursor = scores_collection.find(
            {}, 
            {"_id": 0, "created_at": 0}
        ).sort("time", 1).limit(limit)
        
        leaderboard = await cursor.to_list(length=limit)
        return leaderboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/player/{player_address}")
async def get_player_scores(player_address: str):
    try:
        cursor = scores_collection.find(
            {"player": player_address},
            {"_id": 0, "created_at": 0}
        ).sort("time", 1)
        
        scores = await cursor.to_list(length=None)
        return {
            "player": player_address,
            "total_games": len(scores),
            "best_score": scores[0]["time"] if scores else None,
            "scores": scores
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/verify/{tx_id}")
async def verify_transaction(tx_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://devnet.irys.xyz/{tx_id}")
            if response.status_code == 200:
                return {
                    "verified": True,
                    "url": f"https://devnet.irys.xyz/{tx_id}"
                }
            else:
                return {"verified": False, "error": "Transaction not found"}
                
    except Exception as e:
        return {"verified": False, "error": str(e)}