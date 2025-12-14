from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional
import logging
from ..config.settings import settings


logger = logging.getLogger(__name__)


class VectorDBService:
    def __init__(self):
        self._client: Optional[QdrantClient] = None
        self.collection_name = "book_content_chunks"
        self._initialized = False

    @property
    def client(self) -> QdrantClient:
        """Lazy initialization of Qdrant client"""
        if self._client is None:
            try:
                logger.info(f"Initializing Qdrant client connection to {settings.qdrant_url}")
                self._client = QdrantClient(
                    url=settings.qdrant_url,
                    api_key=settings.qdrant_api_key,
                    prefer_grpc=True,
                    timeout=10  # 10 second timeout
                )
                self._init_collection()
                self._initialized = True
                logger.info("Qdrant client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Qdrant client: {str(e)}")
                raise
        return self._client

    def _init_collection(self):
        """Initialize the collection if it doesn't exist"""
        try:
            self._client.get_collection(self.collection_name)
            logger.debug(f"Collection '{self.collection_name}' already exists")
        except Exception as e:
            # Create collection if it doesn't exist
            logger.info(f"Collection '{self.collection_name}' not found, creating it...")
            try:
                self._client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=1536,  # OpenAI embedding size
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Collection '{self.collection_name}' created successfully")
            except Exception as create_error:
                logger.error(f"Failed to create collection: {str(create_error)}")
                raise

    def upsert_vectors(self, vectors: List[Dict[str, Any]]):
        """Upsert vectors to the collection"""
        points = []
        for vector_data in vectors:
            points.append(
                models.PointStruct(
                    id=vector_data["id"],
                    vector=vector_data["vector"],
                    payload=vector_data["payload"]
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search_vectors(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )

        return [
            {
                "id": result.id,
                "payload": result.payload,
                "score": result.score
            }
            for result in results
        ]

    def delete_vectors(self, ids: List[str]):
        """Delete vectors by IDs"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(
                points=ids
            )
        )


# Global instance - lazy initialization on first use
vector_db_service = VectorDBService()