"""
Simple end-to-end test for Inline Citation and Source Traceability System
"""
import requests
import json

API_BASE = "http://localhost:8001/api"

# Test scenarios
questions = [
    "What is the molecular formula of TestDrug-X?",
    "What storage conditions are mentioned in the documents?",
    "Tell me about the stability data.",
    "List any analytical methods discussed."
]

session_id = "test_session"


def test_chat_with_citations():
    print("\n--- Testing RAG-enabled Chat with Citations ---")
    for idx, q in enumerate(questions, 1):
        payload = {
            "message": q,
            "use_rag": True,
            "include_citations": True,
            "session_id": session_id
        }
        try:
            resp = requests.post(f"{API_BASE}/chat/message", json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            print(f"\nQuestion {idx}: {q}")
            print("Answer:", data.get('message'))
            cites = data.get('citations') or []
            print(f"Citations returned: {len(cites)}")
            for c in cites:
                print(f"  [{c['id']}] {c['source']} - Page {c['page']}, Chunk {c['chunk_id']}")
                print("    Preview:", c['text'][:100] + '...')
        except Exception as e:
            print(f"Error during request: {e}")


def test_chat_without_citations():
    print("\n--- Testing General Chat without RAG ---")
    payload = {
        "message": "Hello, how are you?",
        "use_rag": False,
        "include_citations": False,
        "session_id": session_id
    }
    try:
        resp = requests.post(f"{API_BASE}/chat/message", json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        print("Response:", data.get('message'))
        cites = data.get('citations') or []
        print("Citations returned:", len(cites))
    except Exception as e:
        print(f"Error during request: {e}")


if __name__ == '__main__':
    test_chat_with_citations()
    test_chat_without_citations()
