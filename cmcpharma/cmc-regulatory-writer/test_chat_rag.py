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
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['data']['message']['text'][:200]}...")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # Test RAG question about uploaded document
    payload = {
        "message": "What is the molecular formula of TestDrug-X?",
        "use_rag": True,
        "include_citations": True
    }
    
    print("Testing RAG question...")
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['data']['message']['text'][:200]}...")
        if data['data'].get('citations'):
            print(f"Citations: {data['data']['citations']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_chat()
