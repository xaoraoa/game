#!/usr/bin/env python3
"""
Test Irys Upload Functionality
"""

import requests
import json
import sys
from datetime import datetime

def test_irys_upload():
    """Test Irys upload functionality"""
    base_url = "http://localhost:8001"
    
    print("🚀 Testing Irys Upload Functionality")
    print("=" * 60)
    
    # Test upload
    print("\n📤 Testing Irys Upload")
    try:
        test_upload = {
            "data": json.dumps({
                "type": "devnet_test",
                "player": "0x1234567890123456789012345678901234567890",
                "test_message": "Testing devnet configuration upload",
                "timestamp": datetime.utcnow().isoformat()
            }),
            "tags": [
                {"name": "Test-Type", "value": "devnet-configuration"},
                {"name": "Environment", "value": "devnet"}
            ],
            "player_address": "0x1234567890123456789012345678901234567890"
        }
        
        response = requests.post(f"{base_url}/api/irys/upload", json=test_upload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            print(f"✅ Transaction ID: {data.get('tx_id')}")
            print(f"✅ Gateway URL: {data.get('gateway_url')}")
            print(f"✅ Network: {data.get('network')}")
            print(f"✅ Blockchain Verified: {data.get('blockchain_verified')}")
            print(f"✅ Irys Upload Success: {data.get('irys_upload_success')}")
            
            if data.get('warning'):
                print(f"⚠️  Warning: {data.get('warning')}")
            
            return True, data
        elif response.status_code == 402:
            data = response.json()
            print(f"💰 Insufficient Balance: {data.get('detail')}")
            print("ℹ️  This confirms the balance issue - account needs funding")
            return False, data
        else:
            print(f"❌ Failed: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, str(e)

if __name__ == "__main__":
    success, result = test_irys_upload()
    if success:
        print("\n🎉 Upload test completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Upload test revealed issues (expected due to balance)")
        sys.exit(1)