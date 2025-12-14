from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ...config.settings import settings


def setup_cors(app: FastAPI):
    """Configure CORS middleware for frontend-backend communication"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Expose headers that frontend might need
        expose_headers=["Access-Control-Allow-Origin"]
    )