from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


# Get the backend directory (parent of src)
BACKEND_DIR = Path(__file__).parent.parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str

    # Database Configuration
    database_url: str

    # Qdrant Configuration
    qdrant_url: str
    qdrant_api_key: Optional[str] = None

    # Application Configuration
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"


settings = Settings()