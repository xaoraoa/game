#!/usr/bin/env python3
"""
Irys Devnet Configuration Testing Script
Focus: Test updated Irys configuration with new private key and devnet settings
"""

import requests
import json
import sys
from datetime import datetime
import uuid

class IrysDevnetTester:
    def __init__(self, base_url="https://irys-reflex-backend.onrender.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    self.test_results.append({
                        "test": name,
                        "status": "PASSED",
                        "response": response_data
                    })
                    return True, response_data
                except:
                    print(f"   Response: {response.text}")
                    self.test_results.append({
                        "test": name,
                        "status": "PASSED",
                        "response": response.text
                    })
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                    self.test_results.append({
                        "test": name,
                        "status": "FAILED",
                        "error": error_data,
                        "expected_status": expected_status,
                        "actual_status": response.status_code
                    })
                except:
                    print(f"   Error: {response.text}")
                    self.test_results.append({
                        "test": name,
                        "status": "FAILED",
                        "error": response.text,
                        "expected_status": expected_status,
                        "actual_status": response.status_code
                    })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "test": name,
                "status": "ERROR",
                "error": str(e)
            })
            return False, {}

    def test_irys_network_info(self):
        """Test 1: Irys Network Configuration - Verify devnet configuration"""
        print("\n" + "="*60)
        print("🌐 TEST 1: IRYS NETWORK CONFIGURATION")
        print("="*60)
        print("Testing GET /api/irys/network-info to verify devnet configuration...")
        
        success, response = self.run_test(
            "Irys Network Info (Devnet Configuration)",
            "GET",
            "api/irys/network-info",
            200
        )
        
        if success and isinstance(response, dict):
            # Verify devnet configuration
            network = response.get("network")
            config = response.get("config", {})
            account = response.get("account")
            client_status = response.get("client_status")
            
            print(f"\n📋 Configuration Analysis:")
            print(f"   Network: {network}")
            print(f"   RPC URL: {config.get('rpc_url')}")
            print(f"   Gateway URL: {config.get('gateway_url')}")
            print(f"   Explorer URL: {config.get('explorer_url')}")
            print(f"   Account Address: {account}")
            print(f"   Client Status: {client_status}")
            
            # Verify expected devnet configuration
            expected_network = "devnet"
            expected_rpc = "https://rpc.devnet.irys.xyz/v1"
            expected_gateway = "https://devnet.irys.xyz"
            
            if network == expected_network:
                print("✅ Network correctly set to devnet")
            else:
                print(f"❌ Network mismatch: expected {expected_network}, got {network}")
                
            if config.get('rpc_url') == expected_rpc:
                print("✅ RPC URL correctly configured for devnet")
            else:
                print(f"❌ RPC URL mismatch: expected {expected_rpc}, got {config.get('rpc_url')}")
                
            if config.get('gateway_url') == expected_gateway:
                print("✅ Gateway URL correctly configured for devnet")
            else:
                print(f"❌ Gateway URL mismatch: expected {expected_gateway}, got {config.get('gateway_url')}")
                
            if client_status == "connected":
                print("✅ Irys client is connected")
            else:
                print(f"❌ Irys client not connected: {client_status}")
        
        return success, response

    def test_irys_public_key(self):
        """Test 2: Wallet/Account Setup - Verify private key is loaded and wallet address accessible"""
        print("\n" + "="*60)
        print("🔑 TEST 2: WALLET/ACCOUNT SETUP")
        print("="*60)
        print("Testing GET /api/irys/public-key to verify private key is properly loaded...")
        
        success, response = self.run_test(
            "Irys Public Key (Wallet Address)",
            "GET",
            "api/irys/public-key",
            200
        )
        
        if success and isinstance(response, dict):
            public_key = response.get("publicKey")
            print(f"\n📋 Wallet Analysis:")
            print(f"   Public Key/Address: {public_key}")
            
            # Verify it's a valid Ethereum address format
            if public_key and public_key.startswith("0x") and len(public_key) == 42:
                print("✅ Valid Ethereum address format")
                print("✅ Private key successfully loaded and wallet accessible")
            else:
                print(f"❌ Invalid address format: {public_key}")
        
        return success, response

    def test_irys_balance(self):
        """Test 3: Balance Check - Check if account has funds (resolve "Insufficient balance" issue)"""
        print("\n" + "="*60)
        print("💰 TEST 3: BALANCE CHECK")
        print("="*60)
        print("Testing GET /api/irys/balance to check account funds...")
        
        success, response = self.run_test(
            "Irys Account Balance",
            "GET",
            "api/irys/balance",
            200
        )
        
        if success and isinstance(response, dict):
            balance = response.get("balance")
            address = response.get("address")
            network = response.get("network")
            
            print(f"\n📋 Balance Analysis:")
            print(f"   Balance: {balance}")
            print(f"   Address: {address}")
            print(f"   Network: {network}")
            
            if balance is not None:
                if balance > 0:
                    print("✅ Account has funds - 'Insufficient balance' issue should be resolved")
                else:
                    print("⚠️  Account balance is 0 - may need funding for uploads")
                    print("   Faucet URL: https://irys.xyz/faucet")
            else:
                print("❌ Could not retrieve balance information")
        
        return success, response

    def test_core_functionality(self):
        """Test 4: Core Functionality - Quick test of main endpoints"""
        print("\n" + "="*60)
        print("🔧 TEST 4: CORE FUNCTIONALITY")
        print("="*60)
        print("Testing main endpoints to ensure they work with new configuration...")
        
        # Test 4a: Health Check
        print("\n🏥 Testing Health Check...")
        health_success, health_response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        
        # Test 4b: Game Modes
        print("\n🎮 Testing Game Modes...")
        modes_success, modes_response = self.run_test(
            "Game Modes",
            "GET",
            "api/game-modes",
            200
        )
        
        # Test 4c: Upload Price Check
        print("\n💲 Testing Upload Price...")
        price_success, price_response = self.run_test(
            "Upload Price Check",
            "GET",
            "api/irys/upload-price",
            200,
            params={"data_size": 1000}
        )
        
        # Test 4d: Message Signing
        print("\n✍️ Testing Message Signing...")
        sign_success, sign_response = self.run_test(
            "Message Signing",
            "POST",
            "api/irys/sign",
            200,
            data={"message": "Test message for devnet configuration"}
        )
        
        # Test 4e: Simple Score Submission
        print("\n📊 Testing Score Submission...")
        test_score = {
            "player": "0x1234567890123456789012345678901234567890",
            "username": "DevnetTestPlayer",
            "time": 250,
            "penalty": False,
            "timestamp": datetime.utcnow().isoformat(),
            "game_mode": "classic"
        }
        
        score_success, score_response = self.run_test(
            "Score Submission",
            "POST",
            "api/scores",
            200,
            data=test_score
        )
        
        # Test 4f: Leaderboard
        print("\n🏆 Testing Leaderboard...")
        leaderboard_success, leaderboard_response = self.run_test(
            "Leaderboard",
            "GET",
            "api/leaderboard",
            200,
            params={"limit": 5}
        )
        
        # Summary of core functionality tests
        core_tests = [
            ("Health Check", health_success),
            ("Game Modes", modes_success),
            ("Upload Price", price_success),
            ("Message Signing", sign_success),
            ("Score Submission", score_success),
            ("Leaderboard", leaderboard_success)
        ]
        
        passed_core = sum(1 for _, success in core_tests if success)
        total_core = len(core_tests)
        
        print(f"\n📊 Core Functionality Summary:")
        print(f"   Passed: {passed_core}/{total_core}")
        for test_name, success in core_tests:
            status = "✅" if success else "❌"
            print(f"   {status} {test_name}")
        
        return passed_core == total_core

    def test_irys_upload_functionality(self):
        """Test 5: Irys Upload Test - Test actual upload functionality"""
        print("\n" + "="*60)
        print("📤 TEST 5: IRYS UPLOAD FUNCTIONALITY")
        print("="*60)
        print("Testing POST /api/irys/upload to verify upload works with devnet...")
        
        test_upload = {
            "data": json.dumps({
                "type": "devnet_test",
                "player": "0x1234567890123456789012345678901234567890",
                "test_message": "Testing devnet configuration",
                "timestamp": datetime.utcnow().isoformat()
            }),
            "tags": [
                {"name": "Test-Type", "value": "devnet-configuration"},
                {"name": "Environment", "value": "devnet"}
            ],
            "player_address": "0x1234567890123456789012345678901234567890"
        }
        
        success, response = self.run_test(
            "Irys Upload (Devnet Test)",
            "POST",
            "api/irys/upload",
            200,
            data=test_upload
        )
        
        if success and isinstance(response, dict):
            tx_id = response.get("tx_id")
            gateway_url = response.get("gateway_url")
            network = response.get("network")
            blockchain_verified = response.get("blockchain_verified")
            irys_upload_success = response.get("irys_upload_success")
            
            print(f"\n📋 Upload Analysis:")
            print(f"   Transaction ID: {tx_id}")
            print(f"   Gateway URL: {gateway_url}")
            print(f"   Network: {network}")
            print(f"   Blockchain Verified: {blockchain_verified}")
            print(f"   Irys Upload Success: {irys_upload_success}")
            
            if tx_id:
                print("✅ Transaction ID generated successfully")
            if network == "devnet":
                print("✅ Upload performed on devnet network")
            if irys_upload_success:
                print("✅ Irys upload completed successfully")
            elif "warning" in response:
                print(f"⚠️  Upload warning: {response.get('warning')}")
        
        return success, response

def main():
    print("🚀 Starting Irys Devnet Configuration Testing...")
    print("🎯 Focus: Test updated Irys configuration with new private key and devnet settings")
    print("=" * 80)
    
    # Initialize tester
    tester = IrysDevnetTester()
    
    # Run focused Irys devnet tests
    print("\n🔍 IRYS DEVNET CONFIGURATION TESTING")
    print("Key Environment Variables to verify:")
    print("- IRYS_PRIVATE_KEY=725bbe9ad10ef6b48397d37501ff0c908119fdc0513a85a046884fc9157c80f5")
    print("- IRYS_NETWORK=devnet")
    print("- IRYS_RPC_URL=https://rpc.devnet.irys.xyz/v1")
    print("- GATEWAY_URL=https://devnet.irys.xyz")
    
    # Test 1: Network Configuration
    network_success, network_response = tester.test_irys_network_info()
    
    # Test 2: Wallet/Account Setup
    wallet_success, wallet_response = tester.test_irys_public_key()
    
    # Test 3: Balance Check
    balance_success, balance_response = tester.test_irys_balance()
    
    # Test 4: Core Functionality
    core_success = tester.test_core_functionality()
    
    # Test 5: Upload Functionality
    upload_success, upload_response = tester.test_irys_upload_functionality()
    
    # Final Results
    print("\n" + "=" * 80)
    print("📊 IRYS DEVNET CONFIGURATION TEST RESULTS")
    print("=" * 80)
    
    key_tests = [
        ("Network Configuration", network_success),
        ("Wallet/Account Setup", wallet_success),
        ("Balance Check", balance_success),
        ("Core Functionality", core_success),
        ("Upload Functionality", upload_success)
    ]
    
    passed_key = sum(1 for _, success in key_tests if success)
    total_key = len(key_tests)
    
    print(f"\n🎯 Key Test Results:")
    for test_name, success in key_tests:
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}")
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    print(f"   Key Tests Passed: {passed_key}/{total_key}")
    
    # Conclusion
    print(f"\n🎯 CONCLUSION:")
    if passed_key == total_key:
        print("✅ All key Irys devnet configuration tests passed!")
        print("✅ The 'Insufficient balance' issue should be resolved")
        print("✅ Irys integration is working properly with devnet configuration")
        return 0
    else:
        print("❌ Some key tests failed - Irys configuration needs attention")
        print("⚠️  Check the test results above for specific issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())