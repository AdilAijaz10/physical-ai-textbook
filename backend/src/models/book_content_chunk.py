from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .database import Base


class BookContentChunk(Base):
    __tablename__ = "book_content_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path = Column(String, nullable=False)  # Path to original Markdown file
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in document
    content = Column(String, nullable=False)  # Chunked content from Markdown
    embedding_id = Column(String)  # Reference to Qdrant vector ID
    metadata = Column(JSON)  # Additional metadata like headings, section info
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())