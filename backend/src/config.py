"""
Configuration module for FitSearch AI
"""
import os

class Settings:
    SERPER_API_KEY: str = os.environ.get("SERPER_API_KEY", "")
    SERP_API_KEY: str = os.environ.get("SERP_API_KEY", "")
    GOOGLE_CSE_ID: str = os.environ.get("GOOGLE_CSE_ID", "")
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    PUBMED_API_KEY: str = os.environ.get("PUBMED_API_KEY", "")
    CACHE_TTL: int = 3600
    MAX_RESULTS: int = 20

settings = Settings()
