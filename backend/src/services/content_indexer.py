from typing import List, Dict, Any
import logging
import os
from pathlib import Path
from .embedding_service import embedding_service
from .vector_db import vector_db_service
from .text_chunker import TextChunker
from .markdown_parser import MarkdownParser
from .base_service import BaseService


logger = logging.getLogger(__name__)


class ContentIndexerService(BaseService):
    """Service for indexing documents into the vector database"""

    def __init__(self):
        super().__init__()
        self.vector_db = vector_db_service
        self.text_chunker = TextChunker()
        self.markdown_parser = MarkdownParser()

    def execute(self, *args, **kwargs) -> Any:
        """Execute indexing operation - not directly used, individual methods are called"""
        raise NotImplementedError("Use specific methods like index_documents")

    def index_documents(self, doc_paths: List[str]) -> Dict[str, Any]:
        """Index a list of documents"""
        try:
            indexed_count = 0
            failed_docs = []
            all_chunks = []

            for doc_path in doc_paths:
                try:
                    # Check if file exists
                    if not os.path.exists(doc_path):
                        logger.warning(f"Document does not exist: {doc_path}")
                        failed_docs.append({"path": doc_path, "error": "File does not exist"})
                        continue

                    # Parse the document
                    content = self._read_file(doc_path)
                    parsed_content = self.markdown_parser.parse(content)

                    # Chunk the content
                    chunks = self.text_chunker.chunk(parsed_content, doc_path)

                    # Process each chunk
                    for i, chunk in enumerate(chunks):
                        # Generate embedding for the chunk
                        embedding = embedding_service.generate_embedding(chunk["content"])

                        # Prepare vector data for upsert
                        vector_data = {
                            "id": f"{Path(doc_path).stem}_{i}",
                            "vector": embedding,
                            "payload": {
                                "file_path": doc_path,
                                "chunk_index": i,
                                "content": chunk["content"],
                                "metadata": chunk.get("metadata", {})
                            }
                        }
                        all_chunks.append(vector_data)

                    indexed_count += 1
                    logger.info(f"Successfully processed document: {doc_path}")

                except Exception as e:
                    logger.error(f"Error processing document {doc_path}: {str(e)}", exc_info=True)
                    failed_docs.append({"path": doc_path, "error": str(e)})

            # Upsert all vectors to the database
            if all_chunks:
                self.vector_db.upsert_vectors(all_chunks)
                logger.info(f"Upserted {len(all_chunks)} chunks to vector database")

            status = "completed" if not failed_docs else "partial"
            if failed_docs:
                logger.warning(f"Failed to process {len(failed_docs)} documents")

            return {
                "indexed_count": indexed_count,
                "status": status,
                "details": {
                    "total_chunks": len(all_chunks),
                    "failed_documents": failed_docs
                }
            }

        except Exception as e:
            self.handle_error(e, "ContentIndexerService.index_documents")

    def _read_file(self, file_path: str) -> str:
        """Read content from a file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def delete_document(self, doc_path: str) -> bool:
        """Delete a document from the index"""
        try:
            # In a real implementation, this would query the vector DB for all chunks from this document
            # and delete them by ID
            logger.info(f"Deleting document from index: {doc_path}")
            # This is a placeholder implementation
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_path}: {str(e)}", exc_info=True)
            return False


# Global instance
content_indexer_service = ContentIndexerService()