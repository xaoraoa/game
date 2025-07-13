import requests
import json
from datetime import datetime
import uuid

class IrysIntegrationTester:
    def __init__(self, base_url="https://640dd7bd-d685-4cbd-8bd1-8e5b28dbc755.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    return True, response_data
                except:
                    print(f"   Response: {response.text}")
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_irys_upload_with_custom_tags(self):
        """Test Irys upload with custom tags"""
        test_upload = {
            "data": json.dumps({
                "type": "leaderboard_score",
                "player": "0xTestPlayer123",
                "score": 150,
                "game_mode": "precision",
                "accuracy": 98.5,
                "timestamp": datetime.utcnow().isoformat()
            }),
            "tags": [
                {"name": "Game-Mode", "value": "precision"},
                {"name": "Score-Type", "value": "leaderboard"},
                {"name": "Accuracy", "value": "98.5"}
            ],
            "player_address": "0xTestPlayer123"
        }
        
        return self.run_test(
            "Upload with Custom Tags",
            "POST",
            "api/irys/upload",
            200,
            data=test_upload
        )

    def test_irys_upload_large_data(self):
        """Test Irys upload with larger data payload"""
        large_data = {
            "type": "game_session",
            "player": "0xLargeDataTest",
            "session_id": str(uuid.uuid4()),
            "games": [
                {"time": 200, "mode": "classic", "penalty": False},
                {"time": 180, "mode": "classic", "penalty": False},
                {"time": 220, "mode": "precision", "accuracy": 95.0},
                {"time": 1500, "mode": "sequence", "targets": 5},
                {"hits": 45, "mode": "endurance", "duration": 60000}
            ],
            "statistics": {
                "total_games": 5,
                "best_time": 180,
                "average_time": 425,
                "modes_played": ["classic", "precision", "sequence", "endurance"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        test_upload = {
            "data": json.dumps(large_data),
            "tags": [
                {"name": "Data-Type", "value": "game-session"},
                {"name": "Games-Count", "value": "5"}
            ],
            "player_address": "0xLargeDataTest"
        }
        
        return self.run_test(
            "Upload Large Data Payload",
            "POST",
            "api/irys/upload",
            200,
            data=test_upload
        )

    def test_score_submission_with_irys_tx(self):
        """Test score submission that includes Irys transaction ID"""
        # First upload to Irys
        upload_data = {
            "data": json.dumps({
                "player": "0xIrysIntegrationTest",
                "score": 175,
                "game_mode": "classic",
                "timestamp": datetime.utcnow().isoformat()
            }),
            "tags": [
                {"name": "Score-Value", "value": "175"}
            ],
            "player_address": "0xIrysIntegrationTest"
        }
        
        success, upload_response = self.run_test(
            "Upload Score Data to Irys",
            "POST",
            "api/irys/upload",
            200,
            data=upload_data
        )
        
        if success and 'tx_id' in upload_response:
            # Now submit score with the transaction ID
            score_data = {
                "player": "0xIrysIntegrationTest",
                "username": "IrysTestUser",
                "time": 175,
                "penalty": False,
                "timestamp": datetime.utcnow().isoformat(),
                "tx_id": upload_response['tx_id'],
                "game_mode": "classic"
            }
            
            return self.run_test(
                "Submit Score with Irys TX ID",
                "POST",
                "api/scores",
                200,
                data=score_data
            )
        else:
            print("❌ Failed to get tx_id from upload, skipping score submission")
            return False, {}

    def test_irys_sign_complex_message(self):
        """Test signing a complex message structure"""
        complex_message = {
            "message": json.dumps({
                "action": "score_verification",
                "player": "0xComplexSignTest",
                "score_data": {
                    "time": 165,
                    "game_mode": "precision",
                    "accuracy": 97.8
                },
                "timestamp": datetime.utcnow().isoformat(),
                "nonce": str(uuid.uuid4())
            })
        }
        
        return self.run_test(
            "Sign Complex Message Structure",
            "POST",
            "api/irys/sign",
            200,
            data=complex_message
        )

    def test_verify_real_irys_transaction(self):
        """Test verifying a transaction that was actually uploaded"""
        # First upload something
        upload_data = {
            "data": json.dumps({
                "test": "verification_test",
                "timestamp": datetime.utcnow().isoformat()
            }),
            "player_address": "0xVerificationTest"
        }
        
        success, upload_response = self.run_test(
            "Upload for Verification Test",
            "POST",
            "api/irys/upload",
            200,
            data=upload_data
        )
        
        if success and 'tx_id' in upload_response:
            # Now try to verify it
            return self.run_test(
                "Verify Uploaded Transaction",
                "GET",
                f"api/verify/{upload_response['tx_id']}",
                200
            )
        else:
            print("❌ Failed to get tx_id from upload, skipping verification")
            return False, {}

    def test_leaderboard_with_irys_verified_scores(self):
        """Test leaderboard showing verified vs unverified scores"""
        return self.run_test(
            "Get Leaderboard with Verification Status",
            "GET",
            "api/leaderboard",
            200,
            params={"limit": 15}
        )

    def test_irys_network_configuration(self):
        """Test that network configuration matches environment"""
        success, response = self.run_test(
            "Verify Network Configuration",
            "GET",
            "api/irys/network-info",
            200
        )
        
        if success:
            # Verify the configuration is correct for testnet
            if response.get('network') == 'testnet':
                config = response.get('config', {})
                expected_urls = {
                    'rpc_url': 'https://rpc.devnet.irys.xyz/v1',
                    'gateway_url': 'https://devnet.irys.xyz',
                    'explorer_url': 'https://testnet.irys.xyz'
                }
                
                all_correct = True
                for key, expected_value in expected_urls.items():
                    if config.get(key) != expected_value:
                        print(f"❌ Network config mismatch: {key} = {config.get(key)}, expected {expected_value}")
                        all_correct = False
                
                if all_correct:
                    print("✅ Network configuration is correct for testnet")
                    return True, response
                else:
                    return False, response
            else:
                print(f"❌ Expected testnet, got {response.get('network')}")
                return False, response
        
        return success, response

def main():
    print("🚀 Starting Comprehensive Irys Blockchain Integration Tests...")
    print("=" * 80)
    
    tester = IrysIntegrationTester()
    
    print("\n🔗 Testing Advanced Irys Blockchain Integration...")
    
    # Test 1: Custom tags upload
    tester.test_irys_upload_with_custom_tags()
    
    # Test 2: Large data payload
    tester.test_irys_upload_large_data()
    
    # Test 3: End-to-end Irys integration (upload + score submission)
    tester.test_score_submission_with_irys_tx()
    
    # Test 4: Complex message signing
    tester.test_irys_sign_complex_message()
    
    # Test 5: Transaction verification
    tester.test_verify_real_irys_transaction()
    
    # Test 6: Leaderboard with verification status
    tester.test_leaderboard_with_irys_verified_scores()
    
    # Test 7: Network configuration validation
    tester.test_irys_network_configuration()
    
    # Print final results
    print("\n" + "=" * 80)
    print(f"📊 Irys Integration Test Results:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Irys integration tests passed!")
        return 0
    else:
        print("⚠️  Some Irys integration tests failed!")
        return 1

if __name__ == "__main__":
    main()