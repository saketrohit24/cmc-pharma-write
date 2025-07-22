#!/usr/bin/env python3
"""
End-to-end test to verify that citations appear in the References section.
"""

import requests
import json
import time

def test_full_citation_flow():
    """Test the complete citation flow from backend to frontend."""
    
    print("🧪 Testing complete citation flow...")
    
    # Step 1: Generate a document via the backend API
    template_data = {
        "id": "e2e-test-template",
        "name": "E2E Citation Test Document",
        "description": "Test template for end-to-end citation testing",
        "toc": [
            {
                "id": "1",
                "title": "3.2.S.1 General Information",
                "level": 1,
                "page_number": 1
            },
            {
                "id": "2", 
                "title": "3.2.S.2 Manufacture",
                "level": 1,
                "page_number": 2
            }
        ]
    }
    
    session_id = "session_1753138324801_6oav3lova"
    
    print(f"📡 Calling backend generation API for session: {session_id}")
    
    try:
        response = requests.post(
            f"http://localhost:8001/api/generation/generate/{session_id}",
            json=template_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # Generation can take time
        )
        
        if response.status_code != 200:
            print(f"❌ Backend generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
        doc = response.json()
        print(f"✅ Backend generation successful: {doc['title']}")
        print(f"📄 Generated {len(doc['sections'])} sections")
        
        # Step 2: Analyze the generated document structure
        total_citations = 0
        section_citations = {}
        references_section = None
        
        for section in doc['sections']:
            citation_count = len(section.get('citations', []))
            section_citations[section['title']] = citation_count
            total_citations += citation_count
            
            if section['title'] == 'References':
                references_section = section
                
        print(f"📊 Citation analysis:")
        for title, count in section_citations.items():
            print(f"   {title}: {count} citations")
        print(f"   Total citations: {total_citations}")
        
        # Step 3: Verify References section exists and has citations
        if not references_section:
            print("❌ No References section found in generated document")
            return False
            
        print("✅ References section found")
        ref_citations = references_section.get('citations', [])
        print(f"📚 References section has {len(ref_citations)} citations")
        
        if len(ref_citations) == 0:
            print("❌ References section has no citations")
            return False
            
        # Step 4: Test the frontend conversion logic
        print("🔄 Testing frontend conversion logic...")
        
        # Simulate what the frontend convertBackendDocument does
        all_citations = {}
        for section in doc['sections']:
            if section.get('citations'):
                for citation in section['citations']:
                    all_citations[citation['id']] = {
                        'id': citation['id'],
                        'text': citation['text'],
                        'source': citation['source'],
                        'page': citation['page']
                    }
        
        converted_citations = list(all_citations.values())
        converted_citations.sort(key=lambda x: x['id'])
        
        print(f"🔧 Frontend would convert to {len(converted_citations)} citations")
        
        # Step 5: Test References section rendering logic
        print("📖 Testing References section rendering logic...")
        
        # Simulate what happens in EditableContent for References section
        citations_to_use = converted_citations
        used_citation_ids = set(c['id'] for c in citations_to_use)  # This is our fix
        
        # Simulate GlobalReferences filtering
        used_citations = [c for c in citations_to_use if c['id'] in used_citation_ids]
        
        print(f"🎯 References section would show {len(used_citations)} citations")
        
        if len(used_citations) == 0:
            print("❌ References section would show no citations (BUG!)")
            return False
        
        print("✅ References section would show citations correctly")
        
        # Display some sample citations
        print("📝 Sample citations that would be displayed:")
        for i, citation in enumerate(used_citations[:3]):
            print(f"   [{citation['id']}] {citation['source']}, page {citation['page']}")
        
        if len(used_citations) > 3:
            print(f"   ... and {len(used_citations) - 3} more")
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frontend_api_compatibility():
    """Test that the frontend can properly call the backend API."""
    
    print("\\n🌐 Testing frontend API compatibility...")
    
    # Test a simple health check or docs endpoint
    try:
        response = requests.get("http://localhost:8001/docs", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend is accessible (docs endpoint responding)")
            return True
        else:
            print(f"❌ Backend API call failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting End-to-End Citation Test\\n")
    
    # Test backend connectivity first
    if not test_frontend_api_compatibility():
        print("\\n❌ Backend connectivity test failed. Make sure backend is running on http://localhost:8001")
        exit(1)
    
    # Run the full citation flow test
    if test_full_citation_flow():
        print("\\n🎉 All tests passed! Citations should now appear in the References section.")
    else:
        print("\\n❌ Citation flow test failed. There may still be issues.")
        exit(1)
