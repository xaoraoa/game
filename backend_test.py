import requests
import sys
import json
from datetime import datetime
import uuid

class IrysReflexAPITester:
    def __init__(self, base_url="https://irys-reflex-backend.onrender.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, check_cors=False, origin=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add Origin header for CORS testing
        if origin:
            headers['Origin'] = origin

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if origin:
            print(f"   Origin: {origin}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'OPTIONS':
                response = requests.options(url, headers=headers)

            print(f"   Status Code: {response.status_code}")
            
            # Check CORS headers if requested
            if check_cors:
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                    'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                    'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
                }
                print(f"   CORS Headers: {json.dumps(cors_headers, indent=6)}")
            
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

    # ============================
    # CORS TESTING METHODS
    # ============================
    
    def test_cors_options_health(self):
        """Test CORS preflight request for health endpoint"""
        return self.run_test(
            "CORS OPTIONS - Health Check",
            "OPTIONS",
            "api/health",
            200,
            check_cors=True,
            origin="https://irys-reflex-frontend.onrender.com"
        )
    
    def test_cors_options_game_modes(self):
        """Test CORS preflight request for game modes endpoint"""
        return self.run_test(
            "CORS OPTIONS - Game Modes",
            "OPTIONS",
            "api/game-modes",
            200,
            check_cors=True,
            origin="https://irys-reflex-frontend.onrender.com"
        )
    
    def test_cors_options_scores(self):
        """Test CORS preflight request for scores endpoint"""
        return self.run_test(
            "CORS OPTIONS - Scores",
            "OPTIONS",
            "api/scores",
            200,
            check_cors=True,
            origin="https://irys-reflex-frontend.onrender.com"
        )
    
    def test_cors_get_with_render_origin(self):
        """Test GET request with Render frontend origin"""
        return self.run_test(
            "CORS GET - Health with Render Origin",
            "GET",
            "api/health",
            200,
            check_cors=True,
            origin="https://irys-reflex-frontend.onrender.com"
        )
    
    def test_cors_get_with_localhost_origin(self):
        """Test GET request with localhost origin"""
        return self.run_test(
            "CORS GET - Health with Localhost Origin",
            "GET",
            "api/health",
            200,
            check_cors=True,
            origin="http://localhost:3000"
        )
    
    def test_cors_post_with_render_origin(self):
        """Test POST request with Render frontend origin"""
        test_score = {
            "player": "0x1234567890123456789012345678901234567890",
            "username": "CORSTestPlayer",
            "time": 250,
            "penalty": False,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.run_test(
            "CORS POST - Submit Score with Render Origin",
            "POST",
            "api/scores",
            200,
            data=test_score,
            check_cors=True,
            origin="https://irys-reflex-frontend.onrender.com"
        )
    
    def test_cors_unauthorized_origin(self):
        """Test request with unauthorized origin"""
        return self.run_test(
            "CORS GET - Unauthorized Origin",
            "GET",
            "api/health",
            200,  # Should still work but without CORS headers
            check_cors=True,
            origin="https://malicious-site.com"
        )

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
            "username": "TestPlayer1",
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
            "username": "TestPlayer2",
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
            "username": "TestPlayer3",
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
            "username": "TestUser",
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

    # NEW GAME MODES TESTS
    def test_get_game_modes(self):
        """Test getting available game modes"""
        return self.run_test(
            "Get Game Modes",
            "GET",
            "api/game-modes",
            200
        )

    def test_submit_classic_mode_score(self):
        """Test submitting a classic mode score"""
        test_score = {
            "player": "0x1111111111111111111111111111111111111111",
            "username": "ClassicPlayer",
            "time": 200,
            "penalty": False,
            "timestamp": datetime.utcnow().isoformat(),
            "game_mode": "classic"
        }
        
        return self.run_test(
            "Submit Classic Mode Score",
            "POST",
            "api/scores",
            200,
            data=test_score
        )

    def test_submit_sequence_mode_score(self):
        """Test submitting a sequence mode score"""
        test_score = {
            "player": "0x2222222222222222222222222222222222222222",
            "username": "SequencePlayer",
            "time": 1500,
            "penalty": False,
            "timestamp": datetime.utcnow().isoformat(),
            "game_mode": "sequence",
            "sequence_times": [300, 250, 400, 350, 200],
            "total_targets": 5
        }
        
        return self.run_test(
            "Submit Sequence Mode Score",
            "POST",
            "api/scores",
            200,
            data=test_score
        )

    def test_submit_endurance_mode_score(self):
        """Test submitting an endurance mode score"""
        test_score = {
            "player": "0x3333333333333333333333333333333333333333",
            "username": "EndurancePlayer",
            "time": 60000,  # 60 seconds
            "penalty": False,
            "timestamp": datetime.utcnow().isoformat(),
            "game_mode": "endurance",
            "hits_count": 45,
            "total_targets": 50
        }
        
        return self.run_test(
            "Submit Endurance Mode Score",
            "POST",
            "api/scores",
            200,
            data=test_score
        )

    def test_submit_precision_mode_score(self):
        """Test submitting a precision mode score"""
        test_score = {
            "player": "0x4444444444444444444444444444444444444444",
            "username": "PrecisionPlayer",
            "time": 800,
            "penalty": False,
            "timestamp": datetime.utcnow().isoformat(),
            "game_mode": "precision",
            "accuracy": 92.5,
            "total_targets": 10
        }
        
        return self.run_test(
            "Submit Precision Mode Score",
            "POST",
            "api/scores",
            200,
            data=test_score
        )

    def test_leaderboard_classic_mode(self):
        """Test getting leaderboard filtered by classic mode"""
        return self.run_test(
            "Get Classic Mode Leaderboard",
            "GET",
            "api/leaderboard",
            200,
            params={"game_mode": "classic", "limit": 10}
        )

    def test_leaderboard_sequence_mode(self):
        """Test getting leaderboard filtered by sequence mode"""
        return self.run_test(
            "Get Sequence Mode Leaderboard",
            "GET",
            "api/leaderboard",
            200,
            params={"game_mode": "sequence", "limit": 10}
        )

    def test_leaderboard_endurance_mode(self):
        """Test getting leaderboard filtered by endurance mode"""
        return self.run_test(
            "Get Endurance Mode Leaderboard",
            "GET",
            "api/leaderboard",
            200,
            params={"game_mode": "endurance", "limit": 10}
        )

    def test_leaderboard_precision_mode(self):
        """Test getting leaderboard filtered by precision mode"""
        return self.run_test(
            "Get Precision Mode Leaderboard",
            "GET",
            "api/leaderboard",
            200,
            params={"game_mode": "precision", "limit": 10}
        )

    def test_backward_compatibility_score(self):
        """Test submitting score without game_mode (backward compatibility)"""
        test_score = {
            "player": "0x5555555555555555555555555555555555555555",
            "username": "BackwardCompatPlayer",
            "time": 300,
            "penalty": False,
            "timestamp": datetime.utcnow().isoformat()
            # No game_mode field - should default to "classic"
        }
        
        return self.run_test(
            "Submit Score (Backward Compatibility)",
            "POST",
            "api/scores",
            200,
            data=test_score
        )

    def test_mixed_mode_leaderboard(self):
        """Test getting leaderboard without game_mode filter (all modes)"""
        return self.run_test(
            "Get Mixed Mode Leaderboard",
            "GET",
            "api/leaderboard",
            200,
            params={"limit": 20}
        )

    def test_health_check(self):
        """Test health check endpoint for Render deployment"""
        return self.run_test(
            "Health Check Endpoint",
            "GET",
            "api/health",
            200
        )

    # ============================
    # IRYS BLOCKCHAIN INTEGRATION TESTS
    # ============================

    def test_irys_public_key(self):
        """Test getting Irys public key"""
        return self.run_test(
            "Get Irys Public Key",
            "GET",
            "api/irys/public-key",
            200
        )

    def test_irys_sign_message(self):
        """Test signing a message with Irys private key"""
        test_message = {
            "message": "Test message for signing"
        }
        
        return self.run_test(
            "Sign Message with Irys Key",
            "POST",
            "api/irys/sign",
            200,
            data=test_message
        )

    def test_irys_upload_data(self):
        """Test uploading data to Irys blockchain"""
        test_upload = {
            "data": json.dumps({
                "type": "game_score",
                "player": "0x1234567890123456789012345678901234567890",
                "score": 250,
                "timestamp": datetime.utcnow().isoformat()
            }),
            "tags": [
                {"name": "Game-Type", "value": "reaction-time"},
                {"name": "Score", "value": "250"}
            ],
            "player_address": "0x1234567890123456789012345678901234567890"
        }
        
        return self.run_test(
            "Upload Data to Irys",
            "POST",
            "api/irys/upload",
            200,
            data=test_upload
        )

    def test_irys_network_info(self):
        """Test getting Irys network information"""
        return self.run_test(
            "Get Irys Network Info",
            "GET",
            "api/irys/network-info",
            200
        )

    def test_irys_balance(self):
        """Test getting Irys account balance"""
        return self.run_test(
            "Get Irys Balance",
            "GET",
            "api/irys/balance",
            200
        )

    def test_irys_upload_price(self):
        """Test getting upload price for data"""
        return self.run_test(
            "Get Irys Upload Price",
            "GET",
            "api/irys/upload-price",
            200,
            params={"data_size": 1000}
        )

    def test_irys_fund_account(self):
        """Test funding Irys account"""
        return self.run_test(
            "Fund Irys Account",
            "POST",
            "api/irys/fund",
            200,
            params={"amount": 10000}
        )

    def test_irys_upload_with_custom_tags(self):
        """Test uploading data to Irys with custom tags"""
        test_upload = {
            "data": json.dumps({
                "type": "custom_test",
                "player": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                "custom_field": "test_value",
                "timestamp": datetime.utcnow().isoformat()
            }),
            "tags": [
                {"name": "Test-Type", "value": "custom-upload"},
                {"name": "Version", "value": "1.0"},
                {"name": "Environment", "value": "test"}
            ],
            "player_address": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
        }
        
        return self.run_test(
            "Upload Data with Custom Tags",
            "POST",
            "api/irys/upload",
            200,
            data=test_upload
        )

    def test_irys_upload_large_data(self):
        """Test uploading larger data payload to Irys"""
        large_data = {
            "type": "large_test_data",
            "player": "0x1234567890123456789012345678901234567890",
            "scores": [{"time": i * 100, "penalty": i % 2 == 0} for i in range(100)],
            "metadata": {
                "test_run": "large_data_test",
                "timestamp": datetime.utcnow().isoformat(),
                "description": "Testing large data upload to Irys blockchain"
            }
        }
        
        test_upload = {
            "data": json.dumps(large_data),
            "tags": [
                {"name": "Data-Size", "value": "large"},
                {"name": "Test-Type", "value": "performance"}
            ],
            "player_address": "0x1234567890123456789012345678901234567890"
        }
        
        return self.run_test(
            "Upload Large Data to Irys",
            "POST",
            "api/irys/upload",
            200,
            data=test_upload
        )

    def test_end_to_end_irys_score_flow(self):
        """Test complete flow: Irys upload -> Score submission"""
        print("\n🔄 Testing End-to-End Irys Score Flow...")
        
        # Step 1: Upload score data to Irys
        score_data = {
            "player": "0xe2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2",
            "username": "E2ETestPlayer",
            "time": 175,
            "penalty": False,
            "timestamp": datetime.utcnow().isoformat(),
            "game_mode": "classic"
        }
        
        irys_upload = {
            "data": json.dumps(score_data),
            "tags": [
                {"name": "Content-Type", "value": "game-score"},
                {"name": "Game-Mode", "value": "classic"}
            ],
            "player_address": score_data["player"]
        }
        
        # Upload to Irys first
        success, upload_response = self.run_test(
            "E2E: Upload Score to Irys",
            "POST",
            "api/irys/upload",
            200,
            data=irys_upload
        )
        
        if not success:
            print("❌ E2E Test Failed: Irys upload failed")
            return False, {}
        
        # Extract transaction ID from upload response
        tx_id = upload_response.get("tx_id")
        if not tx_id:
            print("❌ E2E Test Failed: No transaction ID returned from Irys upload")
            return False, {}
        
        print(f"✅ Irys upload successful, tx_id: {tx_id}")
        
        # Step 2: Submit score with Irys transaction ID
        score_data["tx_id"] = tx_id
        
        success, score_response = self.run_test(
            "E2E: Submit Score with Irys TX",
            "POST",
            "api/scores",
            200,
            data=score_data
        )
        
        if success:
            print("✅ End-to-End Irys Score Flow completed successfully!")
            return True, {"upload": upload_response, "score": score_response}
        else:
            print("❌ E2E Test Failed: Score submission failed")
            return False, {}

    def test_irys_sign_complex_message(self):
        """Test signing a complex message structure"""
        complex_message = {
            "message": json.dumps({
                "action": "score_verification",
                "player": "0x1234567890123456789012345678901234567890",
                "score": 150,
                "timestamp": datetime.utcnow().isoformat(),
                "nonce": str(uuid.uuid4())
            })
        }
        
        return self.run_test(
            "Sign Complex Message",
            "POST",
            "api/irys/sign",
            200,
            data=complex_message
        )

    # ============================
    # ACHIEVEMENT SYSTEM TESTS
    # ============================

    def test_get_achievement_types(self):
        """Test getting all available achievement types"""
        return self.run_test(
            "Get Achievement Types",
            "GET",
            "api/achievements/types",
            200
        )

    def test_get_player_achievements_empty(self):
        """Test getting achievements for a player with no achievements"""
        player_address = "0x9999999999999999999999999999999999999999"
        return self.run_test(
            "Get Player Achievements (Empty)",
            "GET",
            f"api/achievements/{player_address}",
            200
        )

    def test_unlock_speed_demon_achievement(self):
        """Test unlocking a speed demon achievement"""
        achievement_data = {
            "id": str(uuid.uuid4()),
            "player": "0x1111111111111111111111111111111111111111",
            "achievement_type": "speed_demon",
            "title": "Speed Demon",
            "description": "React in under 200ms",
            "icon": "⚡",
            "unlocked_at": datetime.utcnow().isoformat()
        }
        
        return self.run_test(
            "Unlock Speed Demon Achievement",
            "POST",
            "api/achievements/unlock",
            200,
            data=achievement_data
        )

    def test_unlock_consistency_master_achievement(self):
        """Test unlocking a consistency master achievement"""
        achievement_data = {
            "id": str(uuid.uuid4()),
            "player": "0x2222222222222222222222222222222222222222",
            "achievement_type": "consistency_master",
            "title": "Consistency Master",
            "description": "10 games within 50ms variance",
            "icon": "🎯",
            "unlocked_at": datetime.utcnow().isoformat()
        }
        
        return self.run_test(
            "Unlock Consistency Master Achievement",
            "POST",
            "api/achievements/unlock",
            200,
            data=achievement_data
        )

    def test_unlock_duplicate_achievement(self):
        """Test unlocking the same achievement twice (should return already_unlocked)"""
        achievement_data = {
            "id": str(uuid.uuid4()),
            "player": "0x1111111111111111111111111111111111111111",
            "achievement_type": "speed_demon",
            "title": "Speed Demon",
            "description": "React in under 200ms",
            "icon": "⚡",
            "unlocked_at": datetime.utcnow().isoformat()
        }
        
        return self.run_test(
            "Unlock Duplicate Achievement",
            "POST",
            "api/achievements/unlock",
            200,
            data=achievement_data
        )

    def test_get_player_achievements_with_data(self):
        """Test getting achievements for a player with achievements"""
        player_address = "0x1111111111111111111111111111111111111111"
        return self.run_test(
            "Get Player Achievements (With Data)",
            "GET",
            f"api/achievements/{player_address}",
            200
        )

    # ============================
    # ENHANCED PLAYER STATS TESTS
    # ============================

    def test_get_player_stats_empty(self):
        """Test getting stats for a player with no games"""
        player_address = "0x8888888888888888888888888888888888888888"
        return self.run_test(
            "Get Player Stats (Empty)",
            "GET",
            f"api/player/{player_address}/stats",
            200
        )

    def test_get_player_stats_with_data(self):
        """Test getting stats for a player with game data"""
        player_address = "0x1111111111111111111111111111111111111111"
        return self.run_test(
            "Get Player Stats (With Data)",
            "GET",
            f"api/player/{player_address}/stats",
            200
        )

    def test_generate_stats_image(self):
        """Test generating shareable stats image data"""
        player_address = "0x1111111111111111111111111111111111111111"
        return self.run_test(
            "Generate Stats Image",
            "POST",
            f"api/player/{player_address}/generate-stats-image",
            200
        )

def main():
    print("🚀 Starting Comprehensive Irys Reflex API Tests (Irys Integration + Achievements)...")
    print("=" * 80)
    
    # Initialize tester
    tester = IrysReflexAPITester()
    
    # Run all tests in sequence
    print("\n📋 Running Backend API Tests:")
    
    # Test 1: Health Check for Render Deployment
    print("\n🏥 Testing Health Check Endpoint...")
    tester.test_health_check()
    
    # Test 2: Irys Blockchain Integration
    print("\n🔗 Testing Irys Blockchain Integration...")
    tester.test_irys_public_key()
    tester.test_irys_network_info()
    tester.test_irys_balance()
    tester.test_irys_upload_price()
    tester.test_irys_fund_account()
    tester.test_irys_sign_message()
    tester.test_irys_sign_complex_message()
    tester.test_irys_upload_data()
    tester.test_irys_upload_with_custom_tags()
    tester.test_irys_upload_large_data()
    tester.test_end_to_end_irys_score_flow()
    
    # Test 3: Achievement System
    print("\n🏆 Testing Achievement System...")
    tester.test_get_achievement_types()
    tester.test_get_player_achievements_empty()
    tester.test_unlock_speed_demon_achievement()
    tester.test_unlock_consistency_master_achievement()
    tester.test_unlock_duplicate_achievement()
    tester.test_get_player_achievements_with_data()
    
    # Test 4: Enhanced Player Stats
    print("\n📊 Testing Enhanced Player Stats...")
    tester.test_get_player_stats_empty()
    tester.test_get_player_stats_with_data()
    tester.test_generate_stats_image()
    
    # Test 5: Game Modes API
    print("\n🎮 Testing Game Modes API...")
    tester.test_get_game_modes()
    
    # Test 6: Enhanced Score Submission with Game Modes
    print("\n📈 Testing Enhanced Score Submission...")
    tester.test_submit_classic_mode_score()
    tester.test_submit_sequence_mode_score()
    tester.test_submit_endurance_mode_score()
    tester.test_submit_precision_mode_score()
    
    # Test 7: Backward Compatibility
    print("\n🔄 Testing Backward Compatibility...")
    tester.test_backward_compatibility_score()
    tester.test_submit_score_without_tx()
    tester.test_submit_score_with_penalty()
    tester.test_submit_score_with_mock_tx()
    
    # Test 8: Enhanced Leaderboard with Game Mode Filtering
    print("\n🏅 Testing Enhanced Leaderboard...")
    tester.test_leaderboard_classic_mode()
    tester.test_leaderboard_sequence_mode()
    tester.test_leaderboard_endurance_mode()
    tester.test_leaderboard_precision_mode()
    tester.test_mixed_mode_leaderboard()
    
    # Test 9: Original functionality
    print("\n🔍 Testing Original Functionality...")
    tester.test_leaderboard_empty()
    tester.test_leaderboard_with_data()
    tester.test_leaderboard_with_limit()
    tester.test_player_scores()
    
    # Test 10: Transaction verification
    print("\n🔐 Testing Transaction Verification...")
    tester.test_verify_transaction_mock()
    tester.test_verify_transaction_invalid()
    
    # Test 11: Invalid data handling
    print("\n❌ Testing Error Handling...")
    tester.test_invalid_score_submission()
    
    # Print final results
    print("\n" + "=" * 80)
    print(f"📊 Final Results:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Irys Integration and Achievement System are working correctly!")
        return 0
    else:
        print("⚠️  Some tests failed! Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())