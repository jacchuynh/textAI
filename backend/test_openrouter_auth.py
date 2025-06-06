#!/usr/bin/env python3
"""
Test OpenRouter API authentication directly
"""

import os
import requests

def test_openrouter_auth():
    api_key = os.environ.get('OPENROUTER_API_KEY')
    
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    # Test basic auth with OpenRouter
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://textrealsai.com",  # Optional: your site URL
        "X-Title": "TextRealmsAI",  # Optional: your app name
    }
    
    payload = {
        "model": "",  # Use account default
        "messages": [
            {"role": "user", "content": "Hello, test message"}
        ],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ OpenRouter API authentication successful")
            return True
        else:
            print(f"❌ OpenRouter API authentication failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing OpenRouter API: {e}")
        return False

if __name__ == "__main__":
    test_openrouter_auth()
