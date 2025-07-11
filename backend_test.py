import requests
import sys
import json
from datetime import datetime
import uuid

class IrysReflexAPITester:
    def __init__(self, base_url="https://f70565c0-4bc9-4b97-8590-9dc9b7c0d0c4.preview.emergentagent.com"):
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

    def test_leaderboard_empty(self):
        """Test getting empty leaderboard"""
        return self.run_test(
            "Get Empty Leaderboard",
            "GET",
            "api/leaderboard",
            200
        )

    def test_submit_score_without_tx(self):
        """Test submitting a score without transaction ID"""
        test_score = {
            "player": "0x1234567890123456789012345678901234567890",
            "time": 250,
            "penalty": False,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.run_test(
            "Submit Score (No TX)",
            "POST",
            "api/scores",
            200,
            data=test_score
        )

    def test_submit_score_with_penalty(self):
        """Test submitting a score with penalty"""
        test_score = {
            "player": "0x9876543210987654321098765432109876543210",
            "time": 500,
            "penalty": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.run_test(
            "Submit Score (With Penalty)",
            "POST",
            "api/scores",
            200,
            data=test_score
        )

    def test_submit_score_with_mock_tx(self):
        """Test submitting a score with mock transaction ID"""
        mock_tx_id = f"mock_tx_{uuid.uuid4().hex[:8]}"
        test_score = {
            "player": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            "time": 180,
            "penalty": False,
            "timestamp": datetime.utcnow().isoformat(),
            "tx_id": mock_tx_id
        }
        
        return self.run_test(
            "Submit Score (With Mock TX)",
            "POST",
            "api/scores",
            200,
            data=test_score
        )

    def test_leaderboard_with_data(self):
        """Test getting leaderboard with data"""
        return self.run_test(
            "Get Leaderboard (With Data)",
            "GET",
            "api/leaderboard",
            200
        )

    def test_leaderboard_with_limit(self):
        """Test getting leaderboard with limit parameter"""
        return self.run_test(
            "Get Leaderboard (Limit 5)",
            "GET",
            "api/leaderboard",
            200,
            params={"limit": 5}
        )

    def test_player_scores(self):
        """Test getting player scores"""
        player_address = "0x1234567890123456789012345678901234567890"
        return self.run_test(
            "Get Player Scores",
            "GET",
            f"api/player/{player_address}",
            200
        )

    def test_verify_transaction_mock(self):
        """Test transaction verification with mock ID"""
        mock_tx_id = "mock_tx_12345"
        return self.run_test(
            "Verify Mock Transaction",
            "GET",
            f"api/verify/{mock_tx_id}",
            200
        )

    def test_verify_transaction_invalid(self):
        """Test transaction verification with invalid ID"""
        invalid_tx_id = "invalid_tx_id_that_does_not_exist"
        return self.run_test(
            "Verify Invalid Transaction",
            "GET",
            f"api/verify/{invalid_tx_id}",
            200  # API returns 200 with verified: false
        )

    def test_invalid_score_submission(self):
        """Test submitting invalid score data"""
        invalid_score = {
            "player": "invalid_address",
            "time": "not_a_number",  # Invalid time
            "penalty": "not_boolean",  # Invalid penalty
            "timestamp": "invalid_timestamp"
        }
        
        return self.run_test(
            "Submit Invalid Score",
            "POST",
            "api/scores",
            422  # Validation error
        )

def main():
    print("🚀 Starting Irys Reflex API Tests...")
    print("=" * 50)
    
    # Initialize tester
    tester = IrysReflexAPITester()
    
    # Run all tests in sequence
    print("\n📋 Running Backend API Tests:")
    
    # Test 1: Empty leaderboard
    tester.test_leaderboard_empty()
    
    # Test 2: Submit scores
    tester.test_submit_score_without_tx()
    tester.test_submit_score_with_penalty()
    tester.test_submit_score_with_mock_tx()
    
    # Test 3: Leaderboard with data
    tester.test_leaderboard_with_data()
    tester.test_leaderboard_with_limit()
    
    # Test 4: Player scores
    tester.test_player_scores()
    
    # Test 5: Transaction verification
    tester.test_verify_transaction_mock()
    tester.test_verify_transaction_invalid()
    
    # Test 6: Invalid data handling
    tester.test_invalid_score_submission()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())