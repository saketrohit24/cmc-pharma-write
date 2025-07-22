#!/usr/bin/env python3
"""
API test for the citation system
"""
import requests
import json
import time

def test_citation_api():
    """Test the citation system via API"""
    
    print("🔗 Testing Citation System via API")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test queries with expected citations
    test_queries = [
        "What is the molecular formula of TestDrug-X?",
        "What are the storage conditions for stability testing?",
        "Tell me about the HPLC analytical method",
        "What is the manufacturing process?"
    ]
    
    print(f"📋 Testing {len(test_queries)} queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 40)
        
        try:
            # Prepare request
            payload = {
                "message": query,
                "use_rag": True,
                "include_citations": True,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            # Send request
            response = requests.post(
                f"{base_url}/api/v1/chat/send",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response text
                message_text = data.get("message", {}).get("text", "No response")
                print(f"🤖 Response: {message_text}")
                
                # Extract citations
                citations = data.get("citations", [])
                if citations:
                    print(f"\n📚 Citations ({len(citations)}):")
                    for citation in citations:
                        if isinstance(citation, dict):
                            print(f"  [{citation.get('id', '?')}] {citation.get('source', 'Unknown')} (Page {citation.get('page', '?')})")
                            print(f"      Chunk ID: {citation.get('chunk_id', 'N/A')}")
                            if 'text' in citation:
                                preview = citation['text'][:100] + "..." if len(citation['text']) > 100 else citation['text']
                                print(f"      Preview: {preview}")
                        else:
                            print(f"  • {citation}")
                else:
                    print("📚 No citations returned")
                
                # Check for inline citation markers
                if any(f"[{j}]" in message_text for j in range(1, 10)):
                    print("✅ Inline citation markers found in response")
                else:
                    print("⚠️  No inline citation markers found")
                    
            else:
                print(f"❌ API request failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - is the server running?")
            print("   Start server with: cd backend && python -m uvicorn app.main:app --reload")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True

def test_server_status():
    """Check if the server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Citation System API Test")
    print("=" * 60)
    
    # Check server status
    if test_server_status():
        time.sleep(1)
        test_citation_api()
    else:
        print("\n💡 To start the server:")
        print("   cd backend")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
