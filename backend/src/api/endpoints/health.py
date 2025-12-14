from fastapi import APIRouter
from typing import Dict, Any
import datetime


router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check endpoint to verify service status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "service": "rag-chatbot-api"
    }


@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check():
    """
    Readiness check endpoint
    """
    # In a real implementation, this would check if all dependencies are ready
    # (database connections, external services, etc.)
    return {
        "status": "ready",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }