#!/usr/bin/env python3
"""
Test script to verify the inline citation and source traceability system
"""
import asyncio
import sys
import os
sys.path.append('backend')

from backend.app.services.chat_service import ChatService
from backend.app.models.chat import ChatRequest

async def test_citation_system():
    """Test the citation system with various queries"""
    
    print("🧪 Testing Inline Citation and Source Traceability System")
    print("=" * 60)
    
    # Initialize chat service
    try:
        chat_service = ChatService()
        print("✅ Chat service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize chat service: {e}")
        return
    
    # Test queries that should trigger citations
    test_queries = [
        "What is the molecular formula of TestDrug-X?",
        "What are the storage conditions for stability testing?", 
        "Tell me about the HPLC method for assay",
        "What are the manufacturing process steps?",
        "What are the specification limits for assay and impurities?"
    ]
    
    print(f"\n📋 Testing {len(test_queries)} queries with citation system...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 50)
        
        try:
            # Create chat request with RAG enabled
            chat_request = ChatRequest(
                message=query,
                use_rag=True,
                include_citations=True,
                max_tokens=500,
                temperature=0.7
            )
            
            # Send message and get response
            response = await chat_service.send_message(chat_request)
            
            # Display results
            print(f"🤖 Response: {response.message.text}")
            
            if response.citations:
                print(f"\n📚 Citations ({len(response.citations)}):")
                for citation in response.citations:
                    if isinstance(citation, dict):
                        print(f"  [{citation.get('id', '?')}] {citation.get('source', 'Unknown')} (Page {citation.get('page', '?')})")
                        print(f"      Chunk ID: {citation.get('chunk_id', 'N/A')}")
                        print(f"      Preview: {citation.get('text', 'N/A')[:100]}...")
                    else:
                        print(f"  • {citation}")
            else:
                print("📚 Citations: None")
                
        except Exception as e:
            print(f"❌ Error testing query: {e}")
    
    # Test RAG service directly
    print(f"\n🔧 Testing RAG service directly...")
    
    try:
        # Ensure RAG is initialized
        await chat_service._ensure_rag_initialized()
        
        if chat_service.rag_service:
            print("✅ RAG service is initialized")
            
            # Test get_relevant_chunks_with_citations method
            if hasattr(chat_service.rag_service, 'get_relevant_chunks_with_citations'):
                docs, citations = chat_service.rag_service.get_relevant_chunks_with_citations(
                    "What is TestDrug-X molecular formula?", 
                    mode="local"
                )
                
                print(f"📄 Retrieved {len(docs)} documents")
                print(f"📚 Generated {len(citations)} citation metadata entries")
                
                for i, citation in enumerate(citations[:3]):  # Show first 3
                    print(f"  Citation {i+1}:")
                    print(f"    ID: {citation.get('id', 'N/A')}")
                    print(f"    File: {citation.get('file', 'N/A')}")
                    print(f"    Page: {citation.get('page', 'N/A')}")
                    print(f"    Chunk ID: {citation.get('chunk_id', 'N/A')}")
                    print(f"    Preview: {citation.get('preview', 'N/A')[:100]}...")
                    
            else:
                print("⚠️  get_relevant_chunks_with_citations method not found")
                
        else:
            print("❌ RAG service not initialized")
            
    except Exception as e:
        print(f"❌ Error testing RAG service: {e}")
    
    print(f"\n🎯 Citation System Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_citation_system())
