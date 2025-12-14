# Implementation Plan: RAG Chatbot for Physical AI & Humanoid Robotics Book

**Branch**: `001-rag-chatbot` | **Date**: 2025-12-14 | **Spec**: [specs/001-rag-chatbot/spec.md](specs/001-rag-chatbot/spec.md)
**Input**: Feature specification from `/specs/001-rag-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build and embed a Retrieval-Augmented Generation (RAG) chatbot into the existing Docusaurus book site. The chatbot will answer user questions about book content by retrieving relevant sections from Markdown docs using OpenAI Agents/ChatKit SDKs, with FastAPI backend, Neon Serverless Postgres, and Qdrant Cloud for vector storage.

## Technical Context

**Language/Version**: Python 3.11 for backend (FastAPI), JavaScript/TypeScript for frontend React component integration with Docusaurus
**Primary Dependencies**: OpenAI SDK, FastAPI, Qdrant client, Neon Postgres driver, React for Docusaurus integration
**Storage**: Neon Serverless Postgres for user sessions/metadata, Qdrant Cloud for book content embeddings
**Testing**: pytest for backend API tests, Jest for frontend component tests, integration tests for RAG functionality
**Target Platform**: Web application (Docusaurus frontend with FastAPI backend)
**Performance Goals**: <5 second response time for queries, handle 100 concurrent users, efficient embedding retrieval
**Constraints**: Free tier limitations for Neon Postgres and Qdrant Cloud, CORS requirements for frontend-backend communication
**Scale/Scope**: Support entire Physical AI & Humanoid Robotics textbook content, handle natural language queries with proper citations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Verify backend service integration guidelines compliance (Principle VII): ✅ API design follows RESTful patterns with FastAPI, proper CORS configurations for frontend integration, and standardized response formats
- Confirm data privacy for RAG queries adherence (Principle VIII): ✅ Encryption of user queries in transit via HTTPS, anonymization of interaction data, session management with appropriate retention policies
- Assess scalability with serverless databases approach (Principle IX): ✅ Neon Serverless Postgres and Qdrant Cloud provide automatic scaling based on demand with pay-per-use model
- Evaluate testing standards for AI-driven features (Principle X): ✅ Implementation includes accuracy benchmarks, response validation, and performance monitoring for the RAG system
- All other existing constitution principles must also be satisfied: ✅ The RAG chatbot enhances educational content accessibility and maintains technical accuracy standards

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── user_session.py
│   │   ├── chat_message.py
│   │   └── query_log.py
│   ├── services/
│   │   ├── rag_service.py
│   │   ├── embedding_service.py
│   │   └── content_indexer.py
│   ├── api/
│   │   ├── main.py
│   │   ├── endpoints/
│   │   │   ├── query.py
│   │   │   ├── index_docs.py
│   │   │   └── health.py
│   │   └── middleware/
│   │       └── cors.py
│   ├── utils/
│   │   ├── text_chunker.py
│   │   └── markdown_parser.py
│   └── config/
│       └── settings.py
└── tests/
    ├── unit/
    │   ├── test_rag_service.py
    │   └── test_embedding_service.py
    ├── integration/
    │   ├── test_query_endpoint.py
    │   └── test_index_docs_endpoint.py
    └── contract/
        └── test_openapi_specs.py

docusaurus/
├── src/
│   └── components/
│       └── RagChatbot/
│           ├── RagChatbot.jsx
│           ├── RagChatbot.css
│           ├── ChatWindow.jsx
│           └── Message.jsx
└── static/
    └── js/
        └── selection-handler.js
```

**Structure Decision**: Web application with separate backend (FastAPI) and Docusaurus frontend integration. The backend handles RAG logic and API endpoints, while the frontend integrates the chatbot as a React component in Docusaurus with additional JavaScript for text selection handling.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
