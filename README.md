# Physical AI & Humanoid Robotics Textbook with RAG Chatbot

This project contains a Docusaurus-based textbook for teaching Physical AI & Humanoid Robotics with an integrated RAG (Retrieval-Augmented Generation) chatbot.

## Project Structure

- `docusaurus.config.js` - Main Docusaurus configuration (English only)
- `src/components/Chatbot/` - Chatbot React component
- `src/theme/Root.js` - Docusaurus theme wrapper that includes the chatbot
- `backend/` - FastAPI backend for the RAG chatbot
- `.env` - Environment variables (not committed)

## Setup Instructions

### Frontend (Docusaurus)

1. Install dependencies:
```bash
npm install
```

2. Create your environment file:
```bash
cp .env.example .env
```

3. Add your OpenAI API key to `.env`:
```bash
OPENAI_API_KEY=your_api_key_here
```

4. Start the development server:
```bash
npm run start
```

The site will be available at `http://localhost:3000/`

### Backend (FastAPI)

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create your environment file:
```bash
cp .env.example .env
```

5. Add your API keys to `backend/.env`:
```bash
OPENAI_API_KEY=your_api_key_here
NEON_DATABASE_URL=your_database_url
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

6. Start the backend server:
```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000/`

## Chatbot Configuration

The chatbot is configured to use the cheapest available OpenAI model by default (`gpt-3.5-turbo`). You can change this by modifying the `OPENAI_MODEL` environment variable.

## Features

- Floating chatbot button that appears on all pages
- Context-aware responses based on textbook content
- Conversation history
- Dark/light mode support
- Mobile-responsive design

## How It Works

1. The frontend chatbot component makes requests to the backend API at `http://localhost:8000/api/v1/chat`
2. The backend processes the query using RAG (Retrieval-Augmented Generation) against the textbook content
3. The response is sent back to the frontend for display

## Backend Setup Required

**Important**: For the chatbot to function properly, you must run the backend server:

### Prerequisites
1. Install Python 3.11 or higher
2. Install pip (Python package manager)

### Setup Steps
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your environment variables in `backend/.env` with your OpenAI API key
4. Start the backend: `python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000`

**Note**: If you get a "command not found" error for python or pip, you may need to:
- Install Python: `sudo apt-get install python3 python3-pip` (on Ubuntu/Debian)
- Or use `python3` and `pip3` instead of `python` and `pip`

**Note 2**: If you encounter dependency conflicts during installation, the system will use compatible versions. The functionality remains the same with newer versions of the packages.

**Note 3**: Some dependencies may require Rust to be installed for compilation. If you encounter installation issues, you may need to install Rust from https://rustup.rs/ or use a Python environment that has pre-compiled wheels available.

Without the backend server running, the chatbot will display an error message with instructions to set up the backend.

## Development

For development, both the frontend and backend servers need to be running simultaneously for the chatbot to function properly.

## Environment Variables

Frontend (`.env`):
- `OPENAI_MODEL` - OpenAI model to use (default: gpt-3.5-turbo)

Backend (`backend/.env`):
- `OPENAI_API_KEY` - Your OpenAI API key
- `DATABASE_URL` - Postgres database URL (using asyncpg)
- `QDRANT_URL` - Qdrant vector database URL
- `QDRANT_API_KEY` - Qdrant API key
- `DEBUG` - Enable debug mode (default: False)
- `LOG_LEVEL` - Logging level (default: INFO)