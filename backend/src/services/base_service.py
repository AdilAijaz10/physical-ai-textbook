from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, Optional
from fastapi import HTTPException


logger = logging.getLogger(__name__)


class BaseService(ABC):
    """Base service class that follows backend service integration guidelines per constitution Principle VII"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data according to standardized validation rules"""
        # Implement standard validation logic
        if not data:
            raise ValueError("Input data cannot be empty")
        return True

    def handle_error(self, error: Exception, context: str = "") -> HTTPException:
        """Handle errors with standardized response formats"""
        error_msg = f"Error in {context}: {str(error)}"
        self.logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

    def format_response(self, data: Any, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Format responses with standardized structure"""
        response = {"data": data}
        if metadata:
            response["metadata"] = metadata
        return response

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the service operation - must be implemented by subclasses"""
        pass