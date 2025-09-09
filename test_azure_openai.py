#!/usr/bin/env python
"""
Test Azure OpenAI Integration
Verifies that the Azure OpenAI credentials in .env are working
"""

import os
import sys
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

def test_azure_openai_connection():
    """Test connection to Azure OpenAI"""
    
    # Get credentials from environment
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    print("🔧 Azure OpenAI Configuration:")
    print(f"   Endpoint: {endpoint}")
    print(f"   Deployment: {deployment}")
    print(f"   API Version: {api_version}")
    print(f"   API Key: {'✓ Set' if api_key else '✗ Missing'}")
    print()
    
    if not all([api_key, endpoint, deployment, api_version]):
        print("❌ Missing required Azure OpenAI configuration")
        return False
    
    # Construct the API URL
    url = f"{endpoint}openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    # Simple test message
    data = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Azure OpenAI is working!' if you can read this."}
        ],
        "max_tokens": 50,
        "temperature": 0
    }
    
    print("🔍 Testing Azure OpenAI connection...")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ Azure OpenAI Response: {message}")
            
            # Print usage info
            if 'usage' in result:
                usage = result['usage']
                print(f"   Tokens used: {usage.get('total_tokens', 'N/A')}")
            
            return True
        else:
            print(f"❌ Azure OpenAI Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 401:
                print("   💡 Check your API key is correct")
            elif response.status_code == 404:
                print("   💡 Check your endpoint and deployment name")
            
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def create_sample_tool_with_openai():
    """Create a sample tool that uses Azure OpenAI"""
    
    tool_code = '''# tools/clinical_text_summarizer.py
"""
Clinical Text Summarizer Tool
Uses Azure OpenAI to summarize clinical text
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def run(input_data: dict) -> dict:
    """
    Summarize clinical text using Azure OpenAI
    
    Args:
        input_data: dict with 'text' key containing clinical text to summarize
    
    Returns:
        dict with 'summary' key containing the summarized text
    """
    
    text = input_data.get('text', '')
    if not text:
        return {"error": "No text provided to summarize"}
    
    # Get Azure OpenAI configuration
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    if not all([api_key, endpoint, deployment, api_version]):
        return {"error": "Azure OpenAI credentials not configured"}
    
    # Prepare the API request
    url = f"{endpoint}openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    data = {
        "messages": [
            {"role": "system", "content": "You are a clinical research assistant. Summarize the following clinical text concisely, preserving key medical information."},
            {"role": "user", "content": text}
        ],
        "max_tokens": 200,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            summary = result['choices'][0]['message']['content']
            return {
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary),
                "tokens_used": result.get('usage', {}).get('total_tokens', 0)
            }
        else:
            return {"error": f"Azure OpenAI API error: {response.status_code}"}
            
    except Exception as e:
        return {"error": f"Failed to summarize text: {str(e)}"}
'''
    
    # Save the tool
    tool_path = "/dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools/tools/clinical_text_summarizer.py"
    
    print("\n📝 Creating sample Azure OpenAI tool...")
    
    try:
        with open(tool_path, 'w') as f:
            f.write(tool_code)
        print(f"✅ Created: {tool_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create tool: {e}")
        return False

def test_clinical_summarizer_tool():
    """Test the clinical text summarizer tool via the API"""
    
    import requests
    
    test_text = """
    Patient is a 45-year-old male presenting with chest pain for 2 days. 
    Pain is substernal, radiating to left arm, associated with shortness of breath.
    Past medical history includes hypertension and diabetes mellitus type 2.
    Current medications: Metformin 1000mg BID, Lisinopril 10mg daily.
    Vital signs: BP 145/90, HR 88, RR 18, Temp 98.6F.
    ECG shows ST elevation in leads II, III, and aVF.
    Troponin I elevated at 2.5 ng/mL.
    """
    
    print("\n🧪 Testing Clinical Text Summarizer tool...")
    
    try:
        response = requests.post(
            "http://127.0.0.1:8210/run_tool/clinical_text_summarizer",
            json={"text": test_text},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if "summary" in result:
                print("✅ Tool response received:")
                print(f"   Original length: {result.get('original_length')} chars")
                print(f"   Summary length: {result.get('summary_length')} chars")
                print(f"   Tokens used: {result.get('tokens_used')}")
                print(f"\n   Summary: {result['summary'][:200]}...")
                return True
            else:
                print(f"❌ Tool error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Azure OpenAI Integration Test")
    print("="*60 + "\n")
    
    # Test 1: Direct Azure OpenAI connection
    if test_azure_openai_connection():
        print("\n✅ Azure OpenAI credentials are valid!")
        
        # Test 2: Create a sample tool
        if create_sample_tool_with_openai():
            
            # Test 3: Test the tool through the API
            test_clinical_summarizer_tool()
    else:
        print("\n❌ Please check your Azure OpenAI credentials in .env")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)

if __name__ == "__main__":
    main()