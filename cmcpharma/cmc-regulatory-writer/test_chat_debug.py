#!/usr/bin/env python3

import requests
import json

# Test the RAG-enabled chat
def test_chat():
    url = "http://localhost:8001/api/chat/message"
    
    # Test general question
    payload = {
        "message": "What is the first president of the United States?",
        "use_rag": False
    }
    
    print("Testing general question...")
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Raw response: {response.text}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"JSON data: {json.dumps(data, indent=2)}")
        except:
            print("Failed to parse JSON")
    
if __name__ == "__main__":
    test_chat()
