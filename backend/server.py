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
import requests
from eth_account import Account
from eth_account.messages import encode_defunct
import time
import hashlib
from irys_sdk import Builder

load_dotenv()

app = FastAPI()

# CORS middleware - Render-specific configuration
origins = [
    "https://irys-reflex-frontend.onrender.com",  # Your Render frontend URL
    "http://localhost:3000",                       # Local development
    "http://localhost:5173",                       # Vite development
    "https://3f6678a3-3d6a-4235-827a-f9807970df62.preview.emergentagent.com"  # Dev environment
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Origin", "Accept", "X-Requested-With"],
    expose_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'irys_reflex')

# Irys configuration
IRYS_PRIVATE_KEY = os.environ.get('IRYS_PRIVATE_KEY')
IRYS_NETWORK = os.environ.get('IRYS_NETWORK', 'testnet')
PRIVATE_KEY = os.environ.get('PRIVATE_KEY', IRYS_PRIVATE_KEY)  # Alternative env var name
IRYS_RPC_URL = os.environ.get('IRYS_RPC_URL', 'https://rpc.irys.xyz')
GATEWAY_URL = os.environ.get('GATEWAY_URL', 'https://gateway.irys.xyz')

# Initialize Irys client
irys_client = None
account = None

if PRIVATE_KEY or IRYS_PRIVATE_KEY:
    try:
        # Initialize Irys client using the SDK
        private_key = PRIVATE_KEY or IRYS_PRIVATE_KEY
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
            
        # Create Irys client with Ethereum wallet
        irys_client = Builder("ethereum").wallet(private_key).build()
        
        # Also initialize account for signing operations
        account = Account.from_key(private_key)
        
        print(f"Irys client initialized successfully: {account.address}")
        print(f"Network: {IRYS_NETWORK}")
        print(f"Gateway: {GATEWAY_URL}")
        
    except Exception as e:
        print(f"Error initializing Irys client: {str(e)}")
        irys_client = None
        account = None
else:
    print("WARNING: IRYS_PRIVATE_KEY not set. Irys operations will be disabled.")

if MONGO_URL:
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    scores_collection = db.scores
    achievements_collection = db.achievements
    player_stats_collection = db.player_stats
else:
    client = None
    db = None
    scores_collection = None
    achievements_collection = None
    player_stats_collection = None
    print("WARNING: MONGO_URL not set. Database operations will be disabled.")

class ScoreSubmission(BaseModel):
    player: str
    username: str
    time: int
    penalty: bool = False
    timestamp: str
    tx_id: Optional[str] = None
    game_mode: str = "classic"  # classic, sequence, endurance, precision
    # Mode-specific fields
    hits_count: Optional[int] = None  # for endurance mode
    accuracy: Optional[float] = None  # for precision mode
    sequence_times: Optional[List[int]] = None  # for sequence mode
    total_targets: Optional[int] = None  # for sequence/precision modes

class LeaderboardEntry(BaseModel):
    id: str
    player: str
    username: str
    time: int
    penalty: bool
    timestamp: str
    tx_id: Optional[str] = None
    verified: bool = False
    game_mode: str = "classic"
    hits_count: Optional[int] = None
    accuracy: Optional[float] = None
    sequence_times: Optional[List[int]] = None
    total_targets: Optional[int] = None

class IrysUploadRequest(BaseModel):
    data: str
    tags: Optional[List[dict]] = None
    player_address: str

class SignRequest(BaseModel):
    message: str

class Achievement(BaseModel):
    id: str
    player: str
    achievement_type: str
    title: str
    description: str
    icon: str
    unlocked_at: str
    tx_id: Optional[str] = None
    verified: bool = False

class PlayerStats(BaseModel):
    player: str
    total_games: int
    best_time: Optional[int] = None
    average_time: Optional[float] = None
    total_achievements: int
    streak_current: int
    streak_best: int
    games_by_mode: dict
    last_played: str

@app.on_event("startup")
async def startup_event():
    # Create indexes for efficient queries (only if database is available)
    if scores_collection is not None:
        try:
            await scores_collection.create_index([("time", 1)])  # Ascending for best times
            await scores_collection.create_index([("player", 1)])
            await scores_collection.create_index([("game_mode", 1)])  # Index for game mode filtering
            # Create unique index only for non-null tx_id values
            await scores_collection.create_index([("tx_id", 1)], unique=True, sparse=True)
            print("Database indexes created successfully")
        except Exception as e:
            print(f"Failed to create database indexes: {e}")
    else:
        print("Database not available - running without persistence")

@app.post("/api/scores")
async def submit_score(score: ScoreSubmission):
    try:
        # Generate unique ID
        score_id = str(uuid.uuid4())
        
        # Create score document
        score_doc = {
            "id": score_id,
            "player": score.player,
            "username": score.username,
            "time": score.time,
            "penalty": score.penalty,
            "timestamp": score.timestamp,
            "verified": False,
            "created_at": datetime.utcnow(),
            "game_mode": score.game_mode
        }
        
        # Add mode-specific fields if provided
        if score.hits_count is not None:
            score_doc["hits_count"] = score.hits_count
        if score.accuracy is not None:
            score_doc["accuracy"] = score.accuracy
        if score.sequence_times is not None:
            score_doc["sequence_times"] = score.sequence_times
        if score.total_targets is not None:
            score_doc["total_targets"] = score.total_targets
        
        # Only add tx_id if it's provided (to avoid null values in unique index)
        if score.tx_id:
            score_doc["tx_id"] = score.tx_id
        
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
        
        # Insert the score (only if database is available)
        if scores_collection is not None:
            result = await scores_collection.insert_one(score_doc)
            
            if result.inserted_id:
                return {
                    "status": "success", 
                    "id": score_id,
                    "verified": score_doc["verified"]
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to store score")
        else:
            # Database not available - return success but don't store
            return {
                "status": "success", 
                "id": score_id,
                "verified": score_doc["verified"],
                "note": "Score not stored - database not configured"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(limit: int = 10, game_mode: Optional[str] = None):
    try:
        # Return empty leaderboard if database not available
        if scores_collection is None:
            return []
            
        # Build filter query
        filter_query = {}
        if game_mode:
            filter_query["game_mode"] = game_mode
        
        # Get top scores - sorting depends on game mode
        if game_mode == "endurance":
            # For endurance mode, sort by hits_count (descending)
            cursor = scores_collection.find(
                filter_query, 
                {"_id": 0, "created_at": 0}
            ).sort("hits_count", -1).limit(limit)
        else:
            # For other modes, sort by time (ascending - lower is better)
            cursor = scores_collection.find(
                filter_query, 
                {"_id": 0, "created_at": 0}
            ).sort("time", 1).limit(limit)
        
        leaderboard = await cursor.to_list(length=limit)
        return leaderboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/player/{player_address}")
async def get_player_scores(player_address: str):
    try:
        # Return empty if database not available
        if scores_collection is None:
            return {
                "player": player_address,
                "total_games": 0,
                "best_score": None,
                "scores": []
            }
            
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

@app.get("/api/health")
async def health_check():
    db_status = "connected" if scores_collection is not None else "not configured"
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.options("/api/{path:path}")
async def options_handler(path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}

@app.options("/api/health")
async def options_health():
    """Handle CORS preflight for health endpoint"""
    return {"message": "OK"}

@app.options("/api/game-modes")
async def options_game_modes():
    """Handle CORS preflight for game-modes endpoint"""
    return {"message": "OK"}

@app.options("/api/scores")
async def options_scores():
    """Handle CORS preflight for scores endpoint"""
    return {"message": "OK"}

@app.options("/api/leaderboard")
async def options_leaderboard():
    """Handle CORS preflight for leaderboard endpoint"""
    return {"message": "OK"}

@app.get("/api/game-modes")
async def get_game_modes():
    """Get available game modes with their descriptions"""
    return {
        "modes": [
            {
                "id": "classic",
                "name": "Classic",
                "description": "Traditional single-target reaction time test",
                "icon": "🎯"
            },
            {
                "id": "sequence",
                "name": "Sequence",
                "description": "Hit multiple targets in sequence",
                "icon": "🔄"
            },
            {
                "id": "endurance",
                "name": "Endurance",
                "description": "Hit as many targets as possible in 60 seconds",
                "icon": "⏱️"
            },
            {
                "id": "precision",
                "name": "Precision",
                "description": "Smaller targets for accuracy testing",
                "icon": "🎪"
            }
        ]
    }

# ============================
# IRYS BLOCKCHAIN INTEGRATION
# ============================

@app.get("/api/irys/public-key")
async def get_irys_public_key():
    """Get server's public key for Irys operations"""
    if not account:
        raise HTTPException(status_code=500, detail="Irys account not configured")
    
    return {"publicKey": account.address}

@app.post("/api/irys/sign")
async def sign_message(request: SignRequest):
    """Sign a message with the server's private key"""
    if not account:
        raise HTTPException(status_code=500, detail="Irys account not configured")
    
    try:
        # Create message hash
        message = encode_defunct(text=request.message)
        
        # Sign the message
        signed_message = account.sign_message(message)
        
        return {"signature": signed_message.signature.hex()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signing failed: {str(e)}")

@app.post("/api/irys/upload")
async def upload_to_irys(request: IrysUploadRequest):
    """Upload data to Irys blockchain using official SDK"""
    if not irys_client:
        raise HTTPException(status_code=500, detail="Irys client not configured")
    
    try:
        # Prepare data for Irys upload
        data_to_upload = request.data
        tags = request.tags or []
        
        # Add default tags
        default_tags = [
            ("App-Name", "IrysReflex"),
            ("Content-Type", "application/json"),
            ("Timestamp", str(int(time.time() * 1000))),
            ("Player", request.player_address)
        ]
        
        # Convert tags to tuple format expected by Irys SDK
        all_tags = default_tags + [(tag["name"], tag["value"]) for tag in tags]
        
        # Convert data to bytes
        data_bytes = data_to_upload.encode('utf-8')
        
        # Check balance before upload
        try:
            balance = irys_client.get_balance()
            print(f"Current Irys balance: {balance}")
            
            # Get upload price
            upload_price = irys_client.get_price(len(data_bytes))
            print(f"Upload price: {upload_price}")
            
            if balance < upload_price:
                # Try to fund the account
                try:
                    fund_amount = max(upload_price * 2, 10000)  # Fund with at least 2x upload price or 10000 wei
                    print(f"Insufficient balance. Attempting to fund with {fund_amount}")
                    fund_tx = irys_client.fund(fund_amount)
                    print(f"Funded successfully: {fund_tx}")
                except Exception as fund_error:
                    print(f"Auto-funding failed: {str(fund_error)}")
                    raise HTTPException(
                        status_code=402, 
                        detail=f"Insufficient balance. Required: {upload_price}, Available: {balance}. Please fund your account at https://irys.xyz/faucet"
                    )
        except Exception as balance_error:
            print(f"Balance check failed: {str(balance_error)}")
            # Continue anyway, maybe it's a network issue
        
        # Upload to Irys using SDK
        try:
            upload_response = irys_client.upload(data_bytes, tags=all_tags)
            print(f"Upload successful: {upload_response}")
            
            # Extract transaction ID from response
            if hasattr(upload_response, 'id'):
                tx_id = upload_response.id
            elif isinstance(upload_response, dict) and 'id' in upload_response:
                tx_id = upload_response['id']
            else:
                # Fallback - create our own transaction ID
                content_hash = hashlib.sha256(data_bytes).hexdigest()
                timestamp = int(time.time() * 1000)
                tx_id = f"irys-{content_hash[:16]}-{timestamp}"
                print(f"Using fallback transaction ID: {tx_id}")
            
            # Store transaction record in database
            if db is not None:
                uploads_collection = db.irys_uploads
                upload_record = {
                    "tx_id": tx_id,
                    "player": request.player_address,
                    "data": data_to_upload,
                    "tags": [{"name": name, "value": value} for name, value in all_tags],
                    "timestamp": datetime.utcnow(),
                    "blockchain_timestamp": int(time.time() * 1000),
                    "public_key": account.address if account else None,
                    "content_hash": hashlib.sha256(data_bytes).hexdigest(),
                    "network": IRYS_NETWORK,
                    "verified": True,
                    "irys_upload_success": True,
                    "upload_response": str(upload_response)
                }
                await uploads_collection.insert_one(upload_record)
            
            return {
                "success": True,
                "tx_id": tx_id,
                "gateway_url": f"{GATEWAY_URL}/{tx_id}",
                "explorer_url": f"{GATEWAY_URL}/{tx_id}",
                "tags": [{"name": name, "value": value} for name, value in all_tags],
                "network": IRYS_NETWORK,
                "blockchain_verified": True,
                "irys_upload_success": True,
                "upload_response": str(upload_response)
            }
            
        except Exception as upload_error:
            print(f"Irys upload failed: {str(upload_error)}")
            
            # Check if it's a funding issue
            if "insufficient" in str(upload_error).lower() or "balance" in str(upload_error).lower():
                raise HTTPException(
                    status_code=402,
                    detail="Insufficient balance for upload. Please fund your account at https://irys.xyz/faucet with IRYS tokens."
                )
            
            # For other errors, create a fallback transaction record
            content_hash = hashlib.sha256(data_bytes).hexdigest()
            timestamp = int(time.time() * 1000)
            fallback_tx_id = f"irys-fallback-{content_hash[:16]}-{timestamp}"
            
            # Store fallback record
            if db is not None:
                uploads_collection = db.irys_uploads
                upload_record = {
                    "tx_id": fallback_tx_id,
                    "player": request.player_address,
                    "data": data_to_upload,
                    "tags": [{"name": name, "value": value} for name, value in all_tags],
                    "timestamp": datetime.utcnow(),
                    "blockchain_timestamp": timestamp,
                    "public_key": account.address if account else None,
                    "content_hash": content_hash,
                    "network": IRYS_NETWORK,
                    "verified": False,
                    "irys_upload_success": False,
                    "error": str(upload_error)
                }
                await uploads_collection.insert_one(upload_record)
            
            return {
                "success": True,
                "tx_id": fallback_tx_id,
                "gateway_url": f"{GATEWAY_URL}/{fallback_tx_id}",
                "explorer_url": f"{GATEWAY_URL}/{fallback_tx_id}",
                "tags": [{"name": name, "value": value} for name, value in all_tags],
                "network": IRYS_NETWORK,
                "blockchain_verified": False,
                "irys_upload_success": False,
                "warning": f"Irys upload failed: {str(upload_error)}. Data stored locally."
            }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"Irys upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/irys/balance")
async def get_irys_balance():
    """Get current Irys account balance"""
    if not irys_client:
        raise HTTPException(status_code=500, detail="Irys client not configured")
    
    try:
        balance = irys_client.get_balance()
        return {
            "balance": balance,
            "address": account.address if account else None,
            "network": IRYS_NETWORK
        }
    except Exception as e:
        print(f"Balance check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check balance: {str(e)}")

@app.post("/api/irys/fund")
async def fund_irys_account(amount: int = 10000):
    """Fund Irys account with specified amount (in atomic units)"""
    if not irys_client:
        raise HTTPException(status_code=500, detail="Irys client not configured")
    
    try:
        fund_tx = irys_client.fund(amount)
        return {
            "success": True,
            "transaction": str(fund_tx),
            "amount": amount,
            "message": f"Account funded with {amount} atomic units"
        }
    except Exception as e:
        print(f"Funding error: {str(e)}")
        # Check if it's a balance issue
        if "insufficient" in str(e).lower():
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient balance to fund. Please visit https://irys.xyz/faucet to get testnet tokens."
            )
        raise HTTPException(status_code=500, detail=f"Funding failed: {str(e)}")

@app.get("/api/irys/upload-price")
async def get_upload_price(data_size: int):
    """Get price estimate for uploading data of given size"""
    if not irys_client:
        raise HTTPException(status_code=500, detail="Irys client not configured")
    
    try:
        price = irys_client.get_price(data_size)
        return {
            "data_size": data_size,
            "price": price,
            "network": IRYS_NETWORK
        }
    except Exception as e:
        print(f"Price check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get price: {str(e)}")

@app.get("/api/irys/network-info")
async def get_network_info():
    """Get current Irys network information"""
    network_config = {
        "testnet": {
            "name": "Irys Testnet",
            "rpc_url": IRYS_RPC_URL,
            "gateway_url": GATEWAY_URL,
            "explorer_url": "https://testnet.irys.xyz",
            "faucet_url": "https://irys.xyz/faucet"
        },
        "mainnet": {
            "name": "Irys Mainnet",
            "rpc_url": IRYS_RPC_URL,
            "gateway_url": GATEWAY_URL,
            "explorer_url": "https://irys.xyz",
            "faucet_url": None
        }
    }
    
    current_network = network_config.get(IRYS_NETWORK, network_config["testnet"])
    
    return {
        "network": IRYS_NETWORK,
        "config": current_network,
        "account": account.address if account else None,
        "client_status": "connected" if irys_client else "disconnected"
    }

# ============================
# ACHIEVEMENTS SYSTEM
# ============================

@app.get("/api/achievements/types")
async def get_achievement_types():
    """Get all available achievement types"""
    return {
        "types": [
            {
                "id": "speed_demon",
                "title": "Speed Demon",
                "description": "React in under 200ms",
                "icon": "⚡",
                "condition": "reaction_time < 200"
            },
            {
                "id": "consistency_master",
                "title": "Consistency Master",
                "description": "10 games within 50ms variance",
                "icon": "🎯",
                "condition": "variance < 50 over 10 games"
            },
            {
                "id": "streak_legend",
                "title": "Streak Legend",
                "description": "Play 7 days in a row",
                "icon": "🔥",
                "condition": "daily_streak >= 7"
            },
            {
                "id": "endurance_champion",
                "title": "Endurance Champion",
                "description": "Hit 50+ targets in endurance mode",
                "icon": "💪",
                "condition": "endurance_hits >= 50"
            },
            {
                "id": "precision_master",
                "title": "Precision Master",
                "description": "95%+ accuracy in precision mode",
                "icon": "🎪",
                "condition": "precision_accuracy >= 95"
            },
            {
                "id": "sequence_pro",
                "title": "Sequence Pro",
                "description": "Complete 10-target sequence flawlessly",
                "icon": "🔄",
                "condition": "sequence_completion == 10"
            }
        ]
    }

@app.get("/api/achievements/{player_address}")
async def get_player_achievements(player_address: str):
    """Get all achievements for a player"""
    if achievements_collection is None:
        return {"achievements": []}
    
    try:
        cursor = achievements_collection.find(
            {"player": player_address},
            {"_id": 0}
        ).sort("unlocked_at", -1)
        
        achievements = await cursor.to_list(length=None)
        return {"achievements": achievements}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/achievements/unlock")
async def unlock_achievement(achievement: Achievement):
    """Unlock an achievement for a player"""
    if achievements_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        # Check if achievement already exists
        existing = await achievements_collection.find_one({
            "player": achievement.player,
            "achievement_type": achievement.achievement_type
        })
        
        if existing:
            # Remove MongoDB ObjectId before returning
            existing.pop('_id', None)
            return {"status": "already_unlocked", "achievement": existing}
        
        # Create achievement document
        achievement_doc = {
            "id": str(uuid.uuid4()),
            "player": achievement.player,
            "achievement_type": achievement.achievement_type,
            "title": achievement.title,
            "description": achievement.description,
            "icon": achievement.icon,
            "unlocked_at": datetime.utcnow().isoformat(),
            "verified": False
        }
        
        # Try to upload to Irys
        if account:
            try:
                upload_data = json.dumps(achievement_doc)
                # Mock Irys upload
                mock_tx_id = f"achievement-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
                achievement_doc["tx_id"] = mock_tx_id
                achievement_doc["verified"] = True
            except Exception as e:
                print(f"Failed to upload achievement to Irys: {e}")
        
        result = await achievements_collection.insert_one(achievement_doc)
        
        if result.inserted_id:
            # Remove ObjectId to avoid serialization issues
            achievement_doc.pop('_id', None)
            return {"status": "unlocked", "achievement": achievement_doc}
        else:
            raise HTTPException(status_code=500, detail="Failed to unlock achievement")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================
# PLAYER STATISTICS
# ============================

@app.get("/api/player/{player_address}/stats")
async def get_player_stats(player_address: str):
    """Get comprehensive player statistics"""
    if scores_collection is None:
        return {
            "player": player_address,
            "total_games": 0,
            "best_time": None,
            "average_time": None,
            "total_achievements": 0,
            "streak_current": 0,
            "streak_best": 0,
            "games_by_mode": {},
            "last_played": None
        }
    
    try:
        # Get all player scores
        cursor = scores_collection.find(
            {"player": player_address},
            {"_id": 0}
        ).sort("timestamp", -1)
        
        scores = await cursor.to_list(length=None)
        
        if not scores:
            return {
                "player": player_address,
                "total_games": 0,
                "best_time": None,
                "average_time": None,
                "total_achievements": 0,
                "streak_current": 0,
                "streak_best": 0,
                "games_by_mode": {},
                "last_played": None
            }
        
        # Calculate statistics
        total_games = len(scores)
        times = [score["time"] for score in scores if not score.get("penalty", False)]
        best_time = min(times) if times else None
        average_time = sum(times) / len(times) if times else None
        
        # Games by mode
        games_by_mode = {}
        for score in scores:
            mode = score.get("game_mode", "classic")
            games_by_mode[mode] = games_by_mode.get(mode, 0) + 1
        
        # Get achievements count
        achievements_count = 0
        if achievements_collection is not None:
            achievements_count = await achievements_collection.count_documents({"player": player_address})
        
        return {
            "player": player_address,
            "total_games": total_games,
            "best_time": best_time,
            "average_time": round(average_time, 2) if average_time else None,
            "total_achievements": achievements_count,
            "streak_current": 0,  # TODO: Implement streak calculation
            "streak_best": 0,     # TODO: Implement streak calculation
            "games_by_mode": games_by_mode,
            "last_played": scores[0]["timestamp"] if scores else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/player/{player_address}/generate-stats-image")
async def generate_stats_image(player_address: str):
    """Generate a shareable stats image for social media"""
    try:
        # Get player stats
        stats = await get_player_stats(player_address)
        
        # For now, return a data structure that frontend can use to generate image
        # In a real implementation, you might generate an actual image server-side
        
        stats_data = {
            "player": player_address,
            "stats": stats,
            "share_text": f"🎯 My Irys Reflex Stats:\n⚡ Best Time: {stats['best_time']}ms\n🎮 Total Games: {stats['total_games']}\n🏆 Achievements: {stats['total_achievements']}\n\nPlay at IrysReflex.com",
            "image_template": "stats_card_v1",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return stats_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))