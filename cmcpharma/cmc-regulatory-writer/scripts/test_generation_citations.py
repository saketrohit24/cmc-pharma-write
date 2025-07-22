"""
Test script to verify citations work in document generation
"""
import requests
import json

API_BASE = "http://localhost:8001/api"

def test_generation_with_citations():
    """Test document generation with citations"""
    
    # Create a simple template with one section
    template = {
        "id": "test_template",
        "name": "Test Document",
        "description": "Test template for citations",
        "toc": [
            {
                "id": "section_1",
                "title": "Protein Particle Analysis",
                "description": "Test section about protein particle analysis methods",
                "level": 1
            }
        ]
    }
    
    # Test document generation using a session with uploaded files
    session_id = "session_1752842836226_2feedjxj8"  # Session with 2 protein particle files
    
    try:
        print("\n🧪 Testing Document Generation with Citations...")
        print("=" * 60)
        
        response = requests.post(
            f"{API_BASE}/generation/generate/{session_id}",
            json=template,
            timeout=60  # Generation takes longer
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Document generation successful!")
            print(f"📄 Document: {data.get('title')}")
            print(f"📝 Sections: {len(data.get('sections', []))}")
            
            # Check each section for citations
            for i, section in enumerate(data.get('sections', []), 1):
                print(f"\n--- Section {i}: {section.get('title')} ---")
                content = section.get('content', '')
                citations = section.get('citations', [])
                
                print(f"Content length: {len(content)} chars")
                print(f"Citations found: {len(citations)}")
                
                # Show first 200 chars of content
                print(f"Content preview: {content[:200]}...")
                
                # Show citations
                if citations:
                    print("📚 Citations:")
                    for cite in citations:
                        print(f"  [{cite['id']}] {cite['source']} - Page {cite['page']}")
                        print(f"      Chunk: {cite['chunk_id']}")
                        print(f"      Preview: {cite['text'][:100]}...")
                else:
                    print("⚠️  No citations found in this section")
                    
        else:
            print(f"❌ Document generation failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == '__main__':
    test_generation_with_citations()
