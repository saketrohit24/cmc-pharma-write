#!/usr/bin/env python3
"""
Test the frontend chat by simulating the exact request the frontend makes
"""

import requests
import json

def test_frontend_chat():
    url = "http://localhost:8001/api/chat/message/stream"
    
    # This matches the request format the frontend should now be sending
    payload = {
        "message": "test my llm",
        "use_rag": True,
        "context": None  # This should avoid the type mismatch
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    print("Testing frontend-style streaming request...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! Streaming response:")
            for i, line in enumerate(response.iter_lines()):
                if line and i < 10:  # Show first 10 lines
                    line_str = line.decode('utf-8')
                    print(f"  {line_str}")
            print("  ...")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_frontend_chat()
