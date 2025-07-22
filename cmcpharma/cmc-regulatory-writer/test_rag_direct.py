#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/rohit/cmcpharma/cmc-regulatory-writer/backend')

from app.services.rag_service import RAGService
from app.core.config import settings
import asyncio

async def test_rag_search():
    # Initialize RAG service with test document
    file_paths = ['/Users/rohit/cmcpharma/cmc-regulatory-writer/backend/persistent_uploads/test_document.txt']
    
    print(f"Testing RAG with file: {file_paths}")
    
    try:
        rag_service = RAGService(file_paths=file_paths, use_graph_rag=False)
        print(f"RAG service initialized successfully")
        print(f"Documents loaded: {len(rag_service.documents)}")
        print(f"Vector store: {rag_service.vector_store}")
        
        if rag_service.vector_store:
            # Test search
            query = "molecular formula TestDrug-X"
            print(f"\nSearching for: {query}")
            results = rag_service.search(query, top_k=3)
            
            print(f"Search results: {len(results) if results else 0}")
            if results:
                for i, result in enumerate(results):
                    print(f"Result {i+1}: {result.page_content[:200]}...")
                    print(f"Metadata: {result.metadata}")
            else:
                print("No results found")
        else:
            print("Vector store not initialized")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_rag_search())
