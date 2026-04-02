"""
Configuration module for Multi-Agent AI Search Platform
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    SERP_API_KEY: Optional[str] = None
    PUBMED_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./database/search_platform.db"
    CHROMA_PERSIST_DIR: str = "./database/chroma"
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # Application
    APP_NAME: str = "FitSearch AI - Multi-Agent Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Search Settings
    MAX_SEARCH_RESULTS: int = 20
    CACHE_TTL_SECONDS: int = 86400  # 24 hours
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Safety Settings
    MAX_DOSAGE_SAFE: bool = True
    ENABLE_SAFETY_CHECKS: bool = True
    
    # Agent Settings
    USE_CLAUDE: bool = True
    USE_GPT4: bool = False
    MAX_CONCURRENT_AGENTS: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
