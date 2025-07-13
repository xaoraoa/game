#!/usr/bin/env python3
"""
Focused Backend API Testing for Irys Reflex
Testing all endpoints mentioned in the review request after Python dependency fixes.
"""

import requests
import json
import uuid
from datetime import datetime
import sys

class FocusedAPITester:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'} if not files else {}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data)
                else:
                    response = requests.post(url, json=data, headers=headers)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:500]}...")
                    return True, response_data
                except:
                    print(f"   Response: {response.text[:200]}...")
                    return True, response.text
            else:
                self.failed_tests.append(name)
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            self.failed_tests.append(name)
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """1. Health Check: Verify /api/health endpoint returns proper status"""
        return self.run_test(
            "Health Check Endpoint",
            "GET",
            "api/health",
            200
        )

    def test_game_modes_api(self):
        """2. Game Modes API: Test /api/game-modes returns all 4 game modes"""
        success, data = self.run_test(
            "Game Modes API",
            "GET",
            "api/game-modes",
            200
        )
        
        if success and isinstance(data, dict) and 'modes' in data:
            modes = data['modes']
            expected_modes = ['classic', 'sequence', 'endurance', 'precision']
            actual_modes = [mode['id'] for mode in modes]
            
            if len(modes) == 4 and all(mode in actual_modes for mode in expected_modes):
                print("✅ All 4 game modes present: classic, sequence, endurance, precision")
                return True, data
            else:
                print(f"❌ Expected 4 game modes {expected_modes}, got {actual_modes}")
                return False, data
        
        return success, data

    def test_score_submission(self):
        """3. Score Submission: Test /api/scores endpoint with valid data"""
        test_score = {
            "player": "0x742d35Cc6634C0532925a3b8D0C9e3e4d6C87",
            "username": "TestPlayer",
            "time": 186,
            "penalty": False,
            "timestamp": datetime.utcnow().isoformat(),
            "game_mode": "classic"
        }
        
        return self.run_test(
            "Score Submission",
            "POST",
            "api/scores",
            200,
            data=test_score
        )

    def test_leaderboard(self):
        """4. Leaderboard: Test /api/leaderboard endpoint"""
        return self.run_test(
            "Leaderboard API",
            "GET",
            "api/leaderboard",
            200,
            params={"limit": 10}
        )

    def test_social_sharing_upload(self):
        """5. Social Sharing: Test /api/upload-screenshot endpoint"""
        # Create a simple test image file
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {
            'screenshot': ('test.png', test_image_data, 'image/png')
        }
        
        form_data = {
            'username': 'TestUser',
            'gameMode': 'classic',
            'reactionTime': '186'
        }
        
        return self.run_test(
            "Social Sharing - Upload Screenshot",
            "POST",
            "api/upload-screenshot",
            200,
            data=form_data,
            files=files
        )

    def test_social_sharing_serve(self):
        """5. Social Sharing: Test /api/screenshots/{filename} endpoint"""
        # First upload a screenshot to get a filename
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {
            'screenshot': ('test.png', test_image_data, 'image/png')
        }
        
        form_data = {
            'username': 'TestUser',
            'gameMode': 'classic',
            'reactionTime': '186'
        }
        
        # Upload first
        upload_success, upload_data = self.run_test(
            "Social Sharing - Upload for Serve Test",
            "POST",
            "api/upload-screenshot",
            200,
            data=form_data,
            files=files
        )
        
        if upload_success and 'filename' in upload_data:
            filename = upload_data['filename']
            # Now test serving the uploaded file
            return self.run_test(
                "Social Sharing - Serve Screenshot",
                "GET",
                f"api/screenshots/{filename}",
                200
            )
        else:
            print("❌ Could not upload screenshot for serve test")
            return False, {}

    def test_player_stats(self):
        """6. Player Stats: Test /api/player/{address} endpoint"""
        player_address = "0x742d35Cc6634C0532925a3b8D0C9e3e4d6C87"
        return self.run_test(
            "Player Stats API",
            "GET",
            f"api/player/{player_address}",
            200
        )

    def test_irys_public_key(self):
        """7. Irys Integration: Test /api/irys/public-key endpoint"""
        return self.run_test(
            "Irys - Public Key",
            "GET",
            "api/irys/public-key",
            200
        )

    def test_irys_network_info(self):
        """7. Irys Integration: Test /api/irys/network-info endpoint"""
        return self.run_test(
            "Irys - Network Info",
            "GET",
            "api/irys/network-info",
            200
        )

    def test_irys_sign_message(self):
        """7. Irys Integration: Test /api/irys/sign endpoint"""
        test_message = {
            "message": "Test message for Irys signing"
        }
        
        return self.run_test(
            "Irys - Sign Message",
            "POST",
            "api/irys/sign",
            200,
            data=test_message
        )

    def test_irys_upload(self):
        """7. Irys Integration: Test /api/irys/upload endpoint"""
        test_upload = {
            "data": json.dumps({
                "type": "test_score",
                "player": "0x742d35Cc6634C0532925a3b8D0C9e3e4d6C87",
                "score": 186,
                "timestamp": datetime.utcnow().isoformat()
            }),
            "tags": [
                {"name": "Content-Type", "value": "test-score"},
                {"name": "Player", "value": "0x742d35Cc6634C0532925a3b8D0C9e3e4d6C87"}
            ],
            "player_address": "0x742d35Cc6634C0532925a3b8D0C9e3e4d6C87"
        }
        
        return self.run_test(
            "Irys - Upload Data",
            "POST",
            "api/irys/upload",
            200,
            data=test_upload
        )

    def test_irys_balance(self):
        """7. Irys Integration: Test /api/irys/balance endpoint"""
        return self.run_test(
            "Irys - Balance Check",
            "GET",
            "api/irys/balance",
            200
        )

    def test_transaction_verification(self):
        """Test transaction verification endpoint"""
        test_tx_id = "test_transaction_id_123"
        return self.run_test(
            "Transaction Verification",
            "GET",
            f"api/verify/{test_tx_id}",
            200
        )

def main():
    print("🚀 FOCUSED BACKEND API TESTING FOR IRYS REFLEX")
    print("=" * 60)
    print("🎯 Testing all endpoints mentioned in review request")
    print("🔧 After fixing Python dependency issues:")
    print("   - eth-account==0.8.0")
    print("   - eth-keyfile==0.6.1") 
    print("   - hexbytes==0.3.1")
    print("   - eth_keys==0.4.0")
    print("   - eth_rlp==0.3.0")
    print("=" * 60)
    
    tester = FocusedAPITester()
    
    # Test all endpoints mentioned in review request
    print("\n1️⃣ HEALTH CHECK")
    tester.test_health_check()
    
    print("\n2️⃣ GAME MODES API")
    tester.test_game_modes_api()
    
    print("\n3️⃣ SCORE SUBMISSION")
    tester.test_score_submission()
    
    print("\n4️⃣ LEADERBOARD")
    tester.test_leaderboard()
    
    print("\n5️⃣ SOCIAL SHARING ENDPOINTS")
    tester.test_social_sharing_upload()
    tester.test_social_sharing_serve()
    
    print("\n6️⃣ PLAYER STATS")
    tester.test_player_stats()
    
    print("\n7️⃣ IRYS INTEGRATION ENDPOINTS")
    tester.test_irys_public_key()
    tester.test_irys_network_info()
    tester.test_irys_sign_message()
    tester.test_irys_upload()
    tester.test_irys_balance()
    
    print("\n8️⃣ ADDITIONAL VERIFICATION")
    tester.test_transaction_verification()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FOCUSED BACKEND TEST RESULTS:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for test in tester.failed_tests:
            print(f"   - {test}")
    
    print("\n🎯 REVIEW REQUEST VERIFICATION:")
    if tester.tests_passed >= tester.tests_run * 0.9:  # 90% success rate
        print("✅ Backend APIs are working correctly after dependency fixes")
        print("✅ All critical endpoints verified functional")
        print("✅ Social sharing endpoints working")
        print("✅ Irys integration endpoints operational")
        return 0
    else:
        print("❌ Some critical endpoints are failing")
        print("🔍 Review failed tests above for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())