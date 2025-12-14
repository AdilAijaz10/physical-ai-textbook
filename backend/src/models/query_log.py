from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .database import Base


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id"), nullable=False)
    query_text = Column(String, nullable=False)
    response_text = Column(String, nullable=False)
    query_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    retrieved_chunks = Column(JSON)  # IDs of content chunks used for response
    response_time_ms = Column(Integer)  # Time taken to generate response