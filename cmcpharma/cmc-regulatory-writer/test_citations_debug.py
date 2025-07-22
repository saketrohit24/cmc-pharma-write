#!/usr/bin/env python3
"""
Test script to verify that citations are being properly returned from backend generation.
"""

import sys
import os
import asyncio
import requests
import json

# Add the backend path to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.rag_service import RAGService
from backend.app.services.generation_service import GenerationService
from backend.app.models.template import Template, TOCItem

async def test_citation_generation():
    """Test that citations are being generated and returned properly."""
    
    print("🔍 Testing citation generation...")
    
    # First, test with sample files in a session directory
    test_session_id = "session_1753138324801_6oav3lova"
    test_files = [
        "/Users/rohit/cmcpharma/cmc-regulatory-writer/backend/persistent_uploads/session_1753138324801_6oav3lova"
    ]
    
    try:
        # Test RAG service citation enrichment
        rag_service = RAGService(file_paths=test_files, use_graph_rag=False)
        generation_service = GenerationService()
        
        # Test a simple section generation
        test_title = "3.2.S.1 General Information"
        print(f"📝 Generating section: {test_title}")
        
        section = await generation_service.synthesize_section(test_title, rag_service)
        
        print(f"✅ Generated section: {section.title}")
        print(f"📊 Content length: {len(section.content)}")
        print(f"🔗 Citations count: {len(section.citations) if section.citations else 0}")
        
        if section.citations:
            print("\n📚 Citations found:")
            for i, citation in enumerate(section.citations):
                print(f"  [{citation.id}] {citation.source}, page {citation.page}")
                print(f"       Preview: {citation.text[:100]}...")
                print(f"       Chunk ID: {citation.chunk_id}")
        else:
            print("❌ No citations found!")
            
        # Check if content has citation markers
        citation_markers = section.content.count('[') + section.content.count(']')
        print(f"🏷️  Citation markers in content: {citation_markers}")
        
        if '[' in section.content and ']' in section.content:
            print("✅ Citation markers found in content")
            # Show some examples
            import re
            markers = re.findall(r'\[(\d+)\]', section.content)
            print(f"   Citation IDs in content: {markers}")
        else:
            print("❌ No citation markers found in content")
            
        return section
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_full_generation_endpoint():
    """Test the full generation endpoint to see if citations are returned."""
    
    print("\n🌐 Testing full generation endpoint...")
    
    # Create a minimal template
    template_data = {
        "id": "test-template",
        "name": "Test Document",
        "description": "Test template for citations",
        "toc": [
            {
                "id": "1",
                "title": "3.2.S.1 General Information",
                "level": 1,
                "page_number": 1
            }
        ]
    }
    
    # Use an existing session with files
    session_id = "session_1753138324801_6oav3lova"
    
    try:
        response = requests.post(
            f"http://localhost:8001/api/generation/generate/{session_id}",
            json=template_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            doc = response.json()
            print(f"✅ Generation successful: {doc['title']}")
            print(f"📄 Sections: {len(doc['sections'])}")
            
            # Check each section for citations
            total_citations = 0
            for i, section in enumerate(doc['sections']):
                citations_count = len(section.get('citations', []))
                total_citations += citations_count
                print(f"  Section {i+1}: {section['title']} - {citations_count} citations")
                
                if citations_count > 0:
                    print("    Citations:")
                    for citation in section['citations']:
                        print(f"      [{citation['id']}] {citation['source']}, p{citation['page']}")
            
            print(f"📊 Total citations across all sections: {total_citations}")
            
            # Check if References section was added
            references_section = next((s for s in doc['sections'] if s['title'] == 'References'), None)
            if references_section:
                print("✅ References section found")
                ref_citations = len(references_section.get('citations', []))
                print(f"   Citations in References section: {ref_citations}")
            else:
                print("❌ No References section found")
                
            return doc
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_citation_generation())
    asyncio.run(test_full_generation_endpoint())
