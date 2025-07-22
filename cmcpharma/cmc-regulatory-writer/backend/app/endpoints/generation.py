from fastapi import APIRouter, Body, HTTPException
from ..models.document import GeneratedDocument, GeneratedSection, RefinementRequest
from ..models.template import Template
from ..services.rag_service import RAGService
from ..services.generation_service import GenerationService
from ..services.file_manager import FileManager
# from ..services.graph_rag_service import RAGConfig  # Temporarily disabled
from ..core.config import settings
from datetime import datetime
import asyncio

router = APIRouter()

@router.post("/generate/{session_id}", response_model=GeneratedDocument)
async def generate_document(session_id: str, template: Template = Body(...)):
    """Generates a full regulatory document based on a template and uploaded files."""
    file_manager = FileManager(session_id)
    file_paths = file_manager.get_session_file_paths()

    if not file_paths:
        raise HTTPException(status_code=400, detail="No source files found for this session.")

    try:
        # Configure GraphRAG if enabled (temporarily disabled)
        graph_rag_config = None
        if settings.USE_GRAPH_RAG:
            print("GraphRAG is temporarily disabled due to dependency issues")
        
        rag_service = RAGService(
            file_paths=file_paths, 
            use_graph_rag=False,  # Disable GraphRAG for now
            graph_rag_config=graph_rag_config
        )
        generation_service = GenerationService()
        
        # Flatten TOC to get all sections (including nested ones)
        def flatten_toc(toc_items):
            flat_items = []
            for item in toc_items:
                flat_items.append(item)
                if hasattr(item, 'children') and item.children:
                    flat_items.extend(flatten_toc(item.children))
            return flat_items
        
        all_sections = flatten_toc(template.toc)
        print(f"Generating {len(all_sections)} sections from template: {[item.title for item in all_sections]}")
        
        # Generate sections sequentially to ensure proper content distribution
        generated_sections = []
        all_citations = []
        
        for i, toc_item in enumerate(all_sections):
            print(f"Generating section {i+1}/{len(all_sections)}: {toc_item.title}")
            section = await generation_service.synthesize_section(toc_item.title, rag_service)
            generated_sections.append(section)
            # Collect all citations
            all_citations.extend(section.citations)
        
        # Automatically add References section if there are any citations
        if all_citations:
            # Deduplicate citations by ID
            unique_citations = {}
            for citation in all_citations:
                if citation.id not in unique_citations:
                    unique_citations[citation.id] = citation
            
            # Create references section with placeholder content
            references_section = GeneratedSection(
                title="References",
                content="<!-- REFERENCES_PLACEHOLDER -->",
                source_count=0,
                citations=list(unique_citations.values())
            )
            generated_sections.append(references_section)
            print(f"Added References section with {len(unique_citations)} unique citations")
        
        print(f"Generated document with {len(generated_sections)} sections")
        
        doc = GeneratedDocument(
            title=template.name,
            template_id=template.id,
            session_id=session_id,
            sections=generated_sections
        )
        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

@router.post("/refine", response_model=dict)
async def refine_section(request: RefinementRequest = Body(...)):
    """Refines a single section of a document based on user feedback."""
    try:
        generation_service = GenerationService()
        refined_content = await generation_service.refine_section(request)
        return {"refined_content": refined_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
