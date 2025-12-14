from typing import List, Dict, Any
import logging
from openai import OpenAI
from .base_service import BaseService
from ..config.settings import settings


logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.openai_api_key)


class EmbeddingService(BaseService):
    """Service for generating and managing embeddings"""

    def __init__(self):
        super().__init__()

    def execute(self, *args, **kwargs) -> Any:
        """Execute embedding operation - not directly used, individual methods are called"""
        raise NotImplementedError("Use specific methods like generate_embedding or generate_embeddings_batch")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate a single embedding for the given text"""
        try:
            response = client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            self.handle_error(e, "EmbeddingService.generate_embedding")

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        try:
            if not texts:
                return []

            # OpenAI API can handle up to 2048 texts in a single request
            # For simplicity, we'll process them individually here
            embeddings = []
            for text in texts:
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)

            return embeddings
        except Exception as e:
            self.handle_error(e, "EmbeddingService.generate_embeddings_batch")

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = sum(a * a for a in embedding1) ** 0.5
        magnitude2 = sum(b * b for b in embedding2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)


# Global instance
embedding_service = EmbeddingService()