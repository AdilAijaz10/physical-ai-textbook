from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from ...services.rag_service import rag_service
import logging
import time
import uuid


# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gpt-3.5-turbo"
    session_id: str = None


class ChatResponse(BaseModel):
    content: str
    session_id: str


@router.post("/chat", response_model=Dict[str, Any])
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint that processes conversation history and returns a response
    """
    start_time = time.time()
    session_id = request.session_id or str(uuid.uuid4())

    try:
        logger.info(f"Processing chat request for session {session_id}")

        # Extract the user's query (last message in the conversation)
        user_query = ""
        for message in reversed(request.messages):
            if message.role == "user":
                user_query = message.content
                break

        if not user_query:
            raise HTTPException(status_code=400, detail="No user message found in conversation")

        # Process the query using RAG service
        result = rag_service.execute(
            query=user_query,
            selected_text=None,  # No selected text in chat context
            session_id=session_id
        )

        # Calculate response time
        response_time = time.time() - start_time
        logger.info(f"Chat processed successfully in {response_time:.2f}s for session {session_id}")

        return {
            "content": result["response"],
            "session_id": session_id
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        logger.warning(f"HTTP error for session {session_id}")
        raise
    except Exception as e:
        # Log the error and raise a generic 500
        response_time = time.time() - start_time
        logger.error(f"Error processing chat for session {session_id} after {response_time:.2f}s: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing chat request")