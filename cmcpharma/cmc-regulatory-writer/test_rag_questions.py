#!/usr/bin/env python3

import requests
import json

# Test the RAG-enabled chat
def test_rag_chat():
    url = "http://localhost:8001/api/chat/message"
    
    # Test RAG question about uploaded document
    payload = {
        "message": "What is the molecular formula of TestDrug-X?",
        "use_rag": True,
        "include_citations": True
    }
    
    print("Testing RAG question about TestDrug-X...")
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response: {data['message']['text']}")
            if data.get('citations'):
                print(f"Citations: {data['citations']}")
            else:
                print("No citations found")
        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Raw response: {response.text}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # Test another RAG question
    payload = {
        "message": "What are the storage conditions for TestDrug-X according to the stability data?",
        "use_rag": True,
        "include_citations": True
    }
    
    print("Testing another RAG question about storage conditions...")
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response: {data['message']['text']}")
            if data.get('citations'):
                print(f"Citations: {data['citations']}")
            else:
                print("No citations found")
        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Raw response: {response.text}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_rag_chat()
