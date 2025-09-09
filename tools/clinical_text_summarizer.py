# tools/clinical_text_summarizer.py
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
