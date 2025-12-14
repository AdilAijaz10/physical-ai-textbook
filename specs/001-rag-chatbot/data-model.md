# Data Model: RAG Chatbot for Physical AI & Humanoid Robotics Book

## Entities

### UserSession
- **id**: UUID (Primary Key)
- **created_at**: DateTime (Timestamp)
- **last_activity**: DateTime (Timestamp)
- **metadata**: JSONB (Additional session data)

### ChatMessage
- **id**: UUID (Primary Key)
- **session_id**: UUID (Foreign Key to UserSession)
- **role**: String (user|assistant)
- **content**: Text (Message content)
- **timestamp**: DateTime (Timestamp)
- **source_citations**: JSONB (Array of source citations from book content)

### BookContentChunk
- **id**: UUID (Primary Key)
- **file_path**: String (Path to original Markdown file)
- **chunk_index**: Integer (Order of chunk in document)
- **content**: Text (Chunked content from Markdown)
- **embedding_id**: String (Reference to Qdrant vector ID)
- **metadata**: JSONB (Additional metadata like headings, section info)

### QueryLog
- **id**: UUID (Primary Key)
- **session_id**: UUID (Foreign Key to UserSession)
- **query_text**: Text (Original user query)
- **response_text**: Text (Generated response)
- **query_timestamp**: DateTime (Timestamp)
- **retrieved_chunks**: JSONB (IDs of content chunks used for response)
- **response_time_ms**: Integer (Time taken to generate response)

## Relationships
- UserSession (1) ←→ (Many) ChatMessage
- UserSession (1) ←→ (Many) QueryLog

## Validation Rules
- UserSession must have a valid UUID
- ChatMessage role must be either 'user' or 'assistant'
- ChatMessage must have a valid session_id reference
- BookContentChunk file_path must exist and be valid
- QueryLog must have valid session_id reference

## State Transitions
- UserSession starts with created_at and transitions to active with last_activity updates
- ChatMessage is immutable once created (append-only log)
- QueryLog is created when a query is processed and never modified