from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from ...services.content_indexer import content_indexer_service


router = APIRouter()


class IndexDocsRequest(BaseModel):
    doc_paths: List[str]


class IndexDocsResponse(BaseModel):
    indexed_count: int
    status: str
    details: Dict[str, Any] = {}


@router.post("/index-docs", response_model=IndexDocsResponse)
async def index_documents(request: IndexDocsRequest):
    """
    Index Docusaurus Markdown documents for RAG retrieval
    """
    try:
        # Validate input
        if not request.doc_paths:
            raise HTTPException(status_code=400, detail="Document paths cannot be empty")

        # Index the documents
        result = content_indexer_service.index_documents(request.doc_paths)

        return IndexDocsResponse(
            indexed_count=result["indexed_count"],
            status=result["status"],
            details=result.get("details", {})
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and raise a generic 500
        import logging
        logging.error(f"Error indexing documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error indexing documents")