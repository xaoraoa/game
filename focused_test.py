import requests
import json
from datetime import datetime
import uuid

def test_focused_endpoints():
    base_url = "https://c315e9bf-e728-49a3-8ec8-e4f5fb435f4a.preview.emergentagent.com"
    
    print("🔍 Testing Achievement Types...")
    response = requests.get(f"{base_url}/api/achievements/types")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    print("\n🔍 Testing Achievement Unlock...")
    achievement_data = {
        "id": str(uuid.uuid4()),
        "player": "0x1111111111111111111111111111111111111111",
        "achievement_type": "speed_demon",
        "title": "Speed Demon",
        "description": "React in under 200ms",
        "icon": "⚡",
        "unlocked_at": datetime.utcnow().isoformat()
    }
    response = requests.post(f"{base_url}/api/achievements/unlock", json=achievement_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    print("\n🔍 Testing Mixed Leaderboard...")
    response = requests.get(f"{base_url}/api/leaderboard", params={"limit": 5})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    print("\n🔍 Testing Player Scores...")
    response = requests.get(f"{base_url}/api/player/0x1111111111111111111111111111111111111111")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_focused_endpoints()