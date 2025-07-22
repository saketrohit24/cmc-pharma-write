from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from ..core.config import settings
# from .graph_rag_service import GraphRAGService, RAGConfig  # Temporarily disabled
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, file_paths: List[str], use_graph_rag: bool = False, graph_rag_config: Optional[Any] = None):
        if not settings.NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY is not set in the environment.")
        
        self.file_paths = file_paths
        self.use_graph_rag = use_graph_rag
        
        print(f"📚 Initializing RAG with {len(self.file_paths)} documents")
        
        # Initialize GraphRAG if enabled
        if self.use_graph_rag:
            print("GraphRAG is temporarily disabled due to dependency issues")
            self.use_graph_rag = False
            self.graph_rag_service = None
        else:
            self.graph_rag_service = None
        
        # Initialize traditional RAG (as fallback or primary)
        if not self.use_graph_rag:
            self.embeddings = NVIDIAEmbeddings(model="nvidia/llama-3.2-nemoretriever-1b-vlm-embed-v1", api_key=settings.NVIDIA_API_KEY)
            self.documents = self._load_and_split_docs()
            self.vector_store = self._create_vector_store()
            self.retriever = self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 20, "fetch_k": 40}
            ) if self.vector_store else None
        else:
            self.embeddings = None
            self.documents = []
            self.vector_store = None
            self.retriever = None

    def _load_and_split_docs(self) -> List[Document]:
        all_pages = []
        for file_path in self.file_paths:
            try:
                # Determine file type and use appropriate loader
                file_extension = os.path.splitext(file_path)[1].lower()
                
                if file_extension == '.pdf':
                    loader = PyPDFLoader(file_path)
                elif file_extension in ['.txt', '.md']:
                    loader = TextLoader(file_path, encoding='utf-8')
                elif file_extension in ['.doc', '.docx']:
                    loader = UnstructuredWordDocumentLoader(file_path)
                else:
                    # Try to load as text file as fallback
                    print(f"Unknown file type {file_extension}, trying as text file: {file_path}")
                    loader = TextLoader(file_path, encoding='utf-8')
                
                pages = loader.load()
                
                # Add enhanced source metadata with page numbers
                for page_idx, page in enumerate(pages):
                    page.metadata['source'] = os.path.basename(file_path)
                    page.metadata['file_path'] = file_path
                    page.metadata['page_number'] = page.metadata.get('page', page_idx + 1)  # Use existing page or index
                    page.metadata['document_id'] = os.path.splitext(os.path.basename(file_path))[0]
                
                all_pages.extend(pages)
                print(f"Successfully loaded {len(pages)} pages from {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"Warning: Could not load {file_path}. Error: {e}")
        
        if not all_pages:
            print("Warning: No documents were successfully loaded.")
            return []
        
        print(f"Total documents loaded: {len(all_pages)}")
        
        # Split documents with enhanced metadata tracking
        splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
        split_docs = splitter.split_documents(all_pages)
        
        # Enrich each chunk with unique chunk ID and enhanced metadata
        for chunk_idx, doc in enumerate(split_docs):
            # Create unique chunk ID
            source_file = doc.metadata.get('document_id', 'unknown')
            page_num = doc.metadata.get('page_number', 1)
            chunk_id = f"{source_file}_p{page_num}_c{chunk_idx}"
            
            # Add citation metadata
            doc.metadata['chunk_id'] = chunk_id
            doc.metadata['chunk_index'] = chunk_idx
            doc.metadata['content_preview'] = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            doc.metadata['word_count'] = len(doc.page_content.split())
        
        print(f"Documents split into {len(split_docs)} chunks with citation metadata")
        return split_docs

    def _create_vector_store(self):
        if not self.documents:
            print("Warning: No documents were loaded. RAG functionality will be disabled.")
            return None
        return FAISS.from_documents(self.documents, self.embeddings)

    def get_relevant_chunks(self, query: str, mode: str = "local") -> List[Document]:
        if self.use_graph_rag and self.graph_rag_service:
            return self.graph_rag_service.get_relevant_chunks(query, mode)
        elif self.retriever:
            return self.retriever.get_relevant_documents(query)
        else:
            print("Warning: No retriever available. RAG is disabled.")
            return []
    
    async def retrieve_relevant_content(self, query: str, file_paths: List[str] = None, top_k: int = 5, mode: str = "local") -> List[dict]:
        """
        Retrieve relevant content for document generation with citation metadata.
        Returns a list of dictionaries with content and source information.
        
        Args:
            query: The search query
            file_paths: Optional filter by file paths (not used in GraphRAG)
            top_k: Number of results to return
            mode: "local" or "global" search mode (only for GraphRAG)
        """
        try:
            if self.use_graph_rag and self.graph_rag_service:
                # Use GraphRAG service
                return await self.graph_rag_service.retrieve_relevant_content(query, file_paths, top_k, mode)
            elif self.retriever:
                # Use traditional RAG with citation support
                docs = self.retriever.get_relevant_documents(query)
                results = []
                for i, doc in enumerate(docs[:top_k]):
                    citation_id = i + 1
                    results.append({
                        'content': doc.page_content,
                        'source': doc.metadata.get('source', f'Document {i+1}'),
                        'metadata': doc.metadata,
                        'citation': {
                            'id': citation_id,
                            'file': doc.metadata.get('source', f'Document {i+1}'),
                            'page': doc.metadata.get('page_number', 1),
                            'chunk_id': doc.metadata.get('chunk_id', f'chunk_{i+1}'),
                            'preview': doc.metadata.get('content_preview', doc.page_content[:100] + "...")
                        }
                    })
                return results
            else:
                print("Warning: No retriever available. RAG is disabled.")
                return []
        except Exception as e:
            print(f"Error retrieving content: {e}")
            return []

    def get_relevant_chunks_with_citations(self, query: str, mode: str = "local") -> tuple[List[Document], List[dict]]:
        """
        Get relevant chunks and return both documents and citation metadata.
        
        Returns:
            tuple: (documents, citations_metadata)
        """
        try:
            if self.use_graph_rag and self.graph_rag_service:
                docs = self.graph_rag_service.get_relevant_chunks(query, mode)
            elif self.retriever:
                docs = self.retriever.get_relevant_documents(query)
            else:
                return [], []
            
            # Create citation metadata
            citations_metadata = []
            unique_sources = set()
            citation_id = 1
            
            for doc in docs:
                # Create unique identifier for deduplication
                source_key = f"{doc.metadata.get('source', 'unknown')}_{doc.metadata.get('chunk_id', 'unknown')}"
                
                if source_key not in unique_sources:
                    unique_sources.add(source_key)
                    citations_metadata.append({
                        'id': citation_id,
                        'file': doc.metadata.get('source', f'Document {citation_id}'),
                        'page': doc.metadata.get('page_number', 1),
                        'chunk_id': doc.metadata.get('chunk_id', f'chunk_{citation_id}'),
                        'preview': doc.metadata.get('content_preview', doc.page_content[:100] + "..."),
                        'content': doc.page_content
                    })
                    citation_id += 1
            
            return docs, citations_metadata
            
        except Exception as e:
            print(f"Error retrieving chunks with citations: {e}")
            return [], []
    
    async def query_with_answer(self, query: str, mode: str = "local") -> Optional[str]:
        """
        Get a complete answer from GraphRAG (if enabled).
        Falls back to None for traditional RAG.
        
        Args:
            query: The search query
            mode: "local" or "global" search mode
        
        Returns:
            Complete answer as string, or None if using traditional RAG
        """
        if self.use_graph_rag and self.graph_rag_service:
            return await self.graph_rag_service.query_with_answer(query, mode)
        return None
    
    def add_documents(self, new_file_paths: List[str]):
        """Add new documents to the RAG system"""
        if self.use_graph_rag and self.graph_rag_service:
            self.graph_rag_service.add_documents(new_file_paths)
        else:
            # For traditional RAG, we'd need to reload everything
            self.file_paths.extend(new_file_paths)
            if self.embeddings:
                self.documents = self._load_and_split_docs()
                self.vector_store = self._create_vector_store()
                self.retriever = self.vector_store.as_retriever(
                    search_type="mmr",
                    search_kwargs={"k": 20, "fetch_k": 40}
                ) if self.vector_store else None