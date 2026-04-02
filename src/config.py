"""
FitSearch AI - Core Configuration
"""
import os

class Settings:
    # API Keys
    SERPER_API_KEY: str = os.environ.get("SERPER_API_KEY", "")
    SERP_API_KEY: str = os.environ.get("SERP_API_KEY", "")
    GOOGLE_CSE_ID: str = os.environ.get("GOOGLE_CSE_ID", "")
    PUBMED_API_KEY: str = os.environ.get("PUBMED_API_KEY", "")
    
    # Server
    PORT: int = int(os.environ.get("PORT", "8000"))
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "production")
    ALLOWED_ORIGINS: str = os.environ.get("ALLOWED_ORIGINS", "*")
    
    # Cache
    CACHE_TTL: int = int(os.environ.get("CACHE_TTL", "3600"))
    MAX_RESULTS: int = int(os.environ.get("MAX_RESULTS", "20"))

settings = Settings()
