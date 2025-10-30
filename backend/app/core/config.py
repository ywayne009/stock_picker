"""Application Configuration"""
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Stock Picking Tool"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/stock_picker"
    REDIS_URL: str = "redis://localhost:6379/0"
    OPENAI_API_KEY: Optional[str] = None
    SECRET_KEY: str = "change-this-key"
    DEFAULT_INITIAL_CAPITAL: float = 100000.0
    
    class Config:
        env_file = ".env"

settings = Settings()
