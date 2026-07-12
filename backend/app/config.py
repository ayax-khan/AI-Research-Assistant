from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "AI Research Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/research_assistant"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "paper_chunks"
    VECTOR_SIZE: int = 1536

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_LLM_MODEL: str = "gpt-4-turbo"

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    GEMINI_LLM_MODEL: str = "gemini-1.5-pro"

    LLM_PROVIDER: str = "openai"

    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5
    TEMPERATURE: float = 0.3

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    OTP_EXPIRE_MINUTES: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
