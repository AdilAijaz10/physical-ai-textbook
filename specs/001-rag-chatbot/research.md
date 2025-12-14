# Research: RAG Chatbot Implementation

## Decision: OpenAI Agents/ChatKit SDKs for chat interface and RAG logic
**Rationale**: OpenAI provides reliable, well-documented APIs for embeddings and chat functionality. Using OpenAI's SDKs ensures compatibility and leverages their optimized infrastructure for semantic search and response generation.
**Alternatives considered**:
- Self-hosted models (more complex, requires significant compute resources)
- Other cloud providers (limited ecosystem integration with Docusaurus)

## Decision: FastAPI for backend API endpoints
**Rationale**: FastAPI provides excellent performance, automatic API documentation (Swagger), strong typing support, and async capabilities ideal for handling multiple concurrent RAG queries.
**Alternatives considered**:
- Flask (slower, less modern)
- Django (overkill for API-only service)

## Decision: Neon Serverless Postgres for metadata storage
**Rationale**: Neon's serverless Postgres offers automatic scaling, pay-per-use pricing, and compatibility with standard Postgres tools while meeting free tier requirements.
**Alternatives considered**:
- SQLite (limited concurrent access)
- MongoDB (would require different skill set)

## Decision: Qdrant Cloud Free Tier for vector storage
**Rationale**: Qdrant is purpose-built for vector similarity search, offers excellent performance for RAG applications, and has a free tier suitable for development.
**Alternatives considered**:
- Pinecone (commercial focus)
- Weaviate (more complex setup)
- ChromaDB (self-hosted requirement)

## Decision: React component integration in Docusaurus
**Rationale**: Docusaurus is built on React, making it natural to integrate custom React components. This allows seamless embedding of the chat interface as a theme component or plugin.
**Alternatives considered**:
- Pure vanilla JavaScript (less integration with Docusaurus ecosystem)
- Web components (more complex styling integration)

## Decision: Markdown indexing during build/deploy
**Rationale**: Parsing and indexing Markdown docs during the build process ensures content is always up-to-date and reduces runtime processing overhead.
**Implementation approach**:
- Parse .md files from Docusaurus content directories
- Chunk text using semantic boundaries
- Generate embeddings via OpenAI API
- Upsert to Qdrant vector database

## Decision: Browser Selection API for selected text queries
**Rationale**: The browser Selection API provides reliable access to user-selected text across different browsers and allows passing this context to the RAG query.
**Implementation approach**:
- Capture selection using window.getSelection()
- Pass selected text as additional context to the RAG query
- Allow users to ask questions specifically about highlighted content

## Decision: Vercel for backend deployment
**Rationale**: Vercel offers excellent serverless deployment with FastAPI support, automatic scaling, and good integration with the broader web development ecosystem.
**Alternatives considered**:
- AWS Lambda (more complex configuration)
- Railway (similar but less established)

## Decision: CORS configuration for frontend-backend communication
**Rationale**: Proper CORS setup is essential for security while allowing communication between Docusaurus frontend and FastAPI backend.
**Implementation approach**:
- Configure CORS middleware in FastAPI
- Specify allowed origins for Docusaurus deployment
- Secure endpoints appropriately

## Decision: Minimal libraries approach with vanilla JS/CSS where possible
**Rationale**: Reduces bundle size, complexity, and potential security vulnerabilities while maintaining performance.
**Implementation approach**:
- Use vanilla JavaScript for core functionality where possible
- Add minimal CSS for styling
- Only add libraries when absolutely necessary