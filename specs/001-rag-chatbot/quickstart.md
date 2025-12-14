# Quickstart: RAG Chatbot for Physical AI & Humanoid Robotics Book

## Overview
This guide will help you set up and run the RAG chatbot for the Physical AI & Humanoid Robotics textbook.

## Prerequisites
- Python 3.11+
- Node.js 18+ (for Docusaurus)
- OpenAI API key
- Neon Postgres account
- Qdrant Cloud account

## Setup

### 1. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Update .env with your credentials:
OPENAI_API_KEY=your_openai_api_key
NEON_DATABASE_URL=your_neon_database_url
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
```

### 2. Backend Setup
```bash
# Navigate to backend directory (will be created)
cd backend

# Install Python dependencies
pip install fastapi uvicorn openai qdrant-client psycopg2-binary python-dotenv

# Run the backend server
uvicorn main:app --reload --port 8000
```

### 3. Frontend Integration
```bash
# The chat component will be integrated into Docusaurus as a theme component
# Build and run Docusaurus
npm install
npm run start
```

### 4. Initial Content Indexing
```bash
# Index all textbook content to vector database
curl -X POST http://localhost:8000/index-docs \
  -H "Content-Type: application/json" \
  -d '{"doc_paths": ["/docs/module1/*.md", "/docs/module2/*.md"]}'
```

## API Usage

### Query the Chatbot
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain how ROS 2 handles message passing between nodes",
    "selected_text": "In ROS 2, nodes communicate through topics, services, and actions...",
    "session_id": "unique-session-id"
  }'
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Frontend Integration
The chat component will be available as a floating window or sidebar in Docusaurus, accessible from any page. Users can:
- Type questions about the textbook content
- Select text and ask questions about the selected content
- View responses with citations to specific book sections
- Minimize/maximize the chat interface

## Development
- Backend server runs on http://localhost:8000
- Frontend runs on http://localhost:3000 (Docusaurus default)
- API documentation available at http://localhost:8000/docs