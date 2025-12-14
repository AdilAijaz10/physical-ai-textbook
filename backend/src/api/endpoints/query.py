from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel, field_validator
from ...services.rag_service import rag_service
from ...models.database import get_db
from ...config.settings import settings
import logging
import time
import uuid


# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    selected_text: str = None
    session_id: str = None

    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        if len(v.strip()) < 3:
            raise ValueError('Query must be at least 3 characters long')
        return v.strip()

    @field_validator('selected_text')
    @classmethod
    def validate_selected_text(cls, v):
        if v is not None and len(v.strip()) > 5000:  # Limit selected text to 5000 chars
            raise ValueError('Selected text is too long (max 5000 characters)')
        return v


class Citation(BaseModel):
    file_path: str
    chunk_index: int
    content_snippet: str
    relevance_score: float


class QueryResponse(BaseModel):
    response: str
    citations: List[Citation]
    session_id: str


@router.post("/query", response_model=Dict[str, Any])
async def process_query(request: QueryRequest):
    """
    Process a user query and return a response with citations
    """
    start_time = time.time()
    session_id = request.session_id or str(uuid.uuid4())

    try:
        logger.info(f"Processing query for session {session_id}: {request.query[:50]}...")

        # Process the query using RAG service
        result = rag_service.execute(
            query=request.query,
            selected_text=request.selected_text,
            session_id=session_id
        )

        # Calculate response time
        response_time = time.time() - start_time
        logger.info(f"Query processed successfully in {response_time:.2f}s for session {session_id}")

        return {
            "response": result["response"],
            "citations": result["citations"],
            "session_id": session_id
        }

    except ValueError as e:
        # Handle validation errors
        logger.warning(f"Validation error for session {session_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Re-raise HTTP exceptions
        logger.warning(f"HTTP error for session {session_id}")
        raise
    except Exception as e:
        # Log the error and raise a generic 500
        response_time = time.time() - start_time
        logger.error(f"Error processing query for session {session_id} after {response_time:.2f}s: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing query")


@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "query"}