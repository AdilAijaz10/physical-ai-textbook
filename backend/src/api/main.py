from fastapi import FastAPI
from .middleware.cors import setup_cors
from .middleware.logging import setup_logging
from ..config.settings import settings


def create_app():
    app = FastAPI(
        title="RAG Chatbot API",
        description="API for the Retrieval-Augmented Generation chatbot for Physical AI & Humanoid Robotics Book",
        version="1.0.0"
    )

    # Setup middleware
    setup_cors(app)
    setup_logging(app)

    # Include API routes
    from .endpoints import query, health, index_docs, chat
    app.include_router(query.router, prefix="/api/v1", tags=["query"])
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(index_docs.router, prefix="/api/v1", tags=["index"])
    app.include_router(chat.router, prefix="/api/v1", tags=["chat"])

    return app


app = create_app()


@app.get("/")
def root():
    return {"message": "RAG Chatbot API is running!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )