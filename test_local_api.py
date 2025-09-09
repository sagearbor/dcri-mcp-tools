#!/usr/bin/env python
"""
Local API Testing Script for DCRI MCP Tools Server
This script tests the Flask server endpoints to verify local setup
"""

import requests
import json
import sys
from datetime import datetime

# Server configuration
BASE_URL = "http://127.0.0.1:8210"

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                print("✅ Health check: Server is running")
                return True
        print(f"❌ Health check failed: {response.status_code}")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Health check failed: Cannot connect to server")
        print("   Make sure the server is running: python server.py")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_echo_tool():
    """Test the echo tool endpoint"""
    test_data = {
        "text": f"Test message at {datetime.now().isoformat()}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/run_tool/test_echo",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("output") == test_data["text"]:
                print(f"✅ Echo tool: Successfully echoed: '{test_data['text']}'")
                return True
            else:
                print(f"❌ Echo tool: Unexpected response: {result}")
                return False
        else:
            print(f"❌ Echo tool failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Echo tool failed: {e}")
        return False

def test_invalid_tool():
    """Test handling of invalid tool names"""
    try:
        response = requests.post(
            f"{BASE_URL}/run_tool/nonexistent_tool",
            json={"test": "data"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 404:
            print("✅ Error handling: Correctly returns 404 for invalid tool")
            return True
        else:
            print(f"❌ Error handling failed: Expected 404, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_sample_size_calculator():
    """Test the sample size calculator tool (if available)"""
    test_data = {
        "confidence_level": 0.95,
        "margin_of_error": 0.05,
        "population_proportion": 0.5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/run_tool/sample_size_calculator",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if "sample_size" in result:
                print(f"✅ Sample size calculator: Calculated size = {result['sample_size']}")
                return True
            else:
                print(f"❌ Sample size calculator: Unexpected response: {result}")
                return False
        elif response.status_code == 404:
            print("⚠️  Sample size calculator: Tool not found (may not be implemented yet)")
            return True  # Not a failure if tool doesn't exist yet
        else:
            print(f"❌ Sample size calculator failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Sample size calculator test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("DCRI MCP Tools - Local API Testing")
    print("="*60 + "\n")
    
    # Check if you can use the Azure OpenAI credentials
    print("📋 Environment Setup Notes:")
    print("   - Your .env file now includes Azure OpenAI credentials")
    print("   - AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, etc.")
    print("   - These can be used by future tools that need LLM capabilities")
    print()
    
    tests = [
        test_health_endpoint,
        test_echo_tool,
        test_invalid_tool,
        test_sample_size_calculator
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("="*60)
    print(f"Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Your local environment is set up correctly.")
        print("\nNext steps:")
        print("1. Update your .env file with real Azure credentials")
        print("2. Test specific tools you want to use")
        print("3. Check logs in the terminal running server.py for details")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)
    
    print("="*60)

if __name__ == "__main__":
    main()