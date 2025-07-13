#!/usr/bin/env python3
"""
Focused Irys Devnet Configuration Test
Testing the updated Irys configuration with new private key and devnet settings
"""

import requests
import json
import sys
from datetime import datetime

def test_irys_configuration():
    """Test the specific Irys configuration endpoints"""
    base_url = "http://localhost:8001"
    results = []
    
    print("🚀 Testing Irys Devnet Configuration")
    print("=" * 60)
    
    # Test 1: Network Configuration
    print("\n🌐 TEST 1: Irys Network Configuration")
    try:
        response = requests.get(f"{base_url}/api/irys/network-info", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Network: {data.get('network')}")
            print(f"✅ RPC URL: {data.get('config', {}).get('rpc_url')}")
            print(f"✅ Gateway URL: {data.get('config', {}).get('gateway_url')}")
            print(f"✅ Account: {data.get('account')}")
            print(f"✅ Client Status: {data.get('client_status')}")
            results.append(("Network Configuration", True, data))
        else:
            print(f"❌ Failed: {response.text}")
            results.append(("Network Configuration", False, response.text))
    except Exception as e:
        print(f"❌ Error: {e}")
        results.append(("Network Configuration", False, str(e)))
    
    # Test 2: Public Key/Wallet
    print("\n🔑 TEST 2: Wallet/Account Setup")
    try:
        response = requests.get(f"{base_url}/api/irys/public-key", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            public_key = data.get('publicKey')
            print(f"✅ Public Key: {public_key}")
            if public_key and public_key.startswith('0x') and len(public_key) == 42:
                print("✅ Valid Ethereum address format")
            results.append(("Wallet Setup", True, data))
        else:
            print(f"❌ Failed: {response.text}")
            results.append(("Wallet Setup", False, response.text))
    except Exception as e:
        print(f"❌ Error: {e}")
        results.append(("Wallet Setup", False, str(e)))
    
    # Test 3: Balance Check
    print("\n💰 TEST 3: Balance Check")
    try:
        response = requests.get(f"{base_url}/api/irys/balance", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            balance = data.get('balance')
            print(f"✅ Balance: {balance}")
            print(f"✅ Address: {data.get('address')}")
            print(f"✅ Network: {data.get('network')}")
            if balance is not None and balance > 0:
                print("✅ Account has funds - 'Insufficient balance' issue resolved!")
            elif balance == 0:
                print("⚠️  Account balance is 0 - may need funding")
            results.append(("Balance Check", True, data))
        else:
            print(f"❌ Failed: {response.text}")
            results.append(("Balance Check", False, response.text))
    except Exception as e:
        print(f"❌ Error: {e}")
        results.append(("Balance Check", False, str(e)))
    
    # Test 4: Upload Price
    print("\n💲 TEST 4: Upload Price Check")
    try:
        response = requests.get(f"{base_url}/api/irys/upload-price?data_size=1000", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Price for 1000 bytes: {data.get('price')}")
            print(f"✅ Network: {data.get('network')}")
            results.append(("Upload Price", True, data))
        else:
            print(f"❌ Failed: {response.text}")
            results.append(("Upload Price", False, response.text))
    except Exception as e:
        print(f"❌ Error: {e}")
        results.append(("Upload Price", False, str(e)))
    
    # Test 5: Message Signing
    print("\n✍️ TEST 5: Message Signing")
    try:
        test_data = {"message": "Test devnet configuration"}
        response = requests.post(f"{base_url}/api/irys/sign", json=test_data, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            signature = data.get('signature')
            print(f"✅ Signature: {signature[:20]}...{signature[-20:] if signature else ''}")
            results.append(("Message Signing", True, data))
        else:
            print(f"❌ Failed: {response.text}")
            results.append(("Message Signing", False, response.text))
    except Exception as e:
        print(f"❌ Error: {e}")
        results.append(("Message Signing", False, str(e)))
    
    # Test 6: Core API Health
    print("\n🏥 TEST 6: Core API Health")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Database: {data.get('database')}")
            results.append(("Core API Health", True, data))
        else:
            print(f"❌ Failed: {response.text}")
            results.append(("Core API Health", False, response.text))
    except Exception as e:
        print(f"❌ Error: {e}")
        results.append(("Core API Health", False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, _ in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All Irys devnet configuration tests passed!")
        print("✅ The updated configuration is working properly")
        return 0
    else:
        print("⚠️  Some tests failed - check configuration")
        return 1

if __name__ == "__main__":
    sys.exit(test_irys_configuration())