from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    STORAGE_BUCKET: str = "documents"
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-sonnet-5-5"
    AI_ENABLED: bool = True
    MAX_UPLOAD_MB: int = 20
    MAX_PAGES: int = 10
    WORKER_CONCURRENCY: int = 2
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    TESSERACT_CMD: Optional[str] = None
    DEV_USER_ID: str = "00000000-0000-0000-0000-000000000001"

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
