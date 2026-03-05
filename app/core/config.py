"""
Core Configuration Module
Centralized configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str
    DB_POOL_MIN_SIZE: int = 2
    DB_POOL_MAX_SIZE: int = 10
    DB_COMMAND_TIMEOUT: int = 30
    
    # News View
    NEWS_VIEW_NAME: str = "vw_news_ar_feed"
    MAX_SNAPSHOT_LIMIT: int = 200
    
    # Processing
    POLL_SECONDS: float = 2.0
    
    # Geocoding
    NOMINATIM_URL: str = "https://nominatim.openstreetmap.org/search"
    GEOCODING_USER_AGENT: str = "GeoNewsAI/1.0 (contact: lmaaljohare@gmail.com)"
    GEOCODING_SLEEP_SECONDS: float = 1.0
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "GeoNews AI"
    PROJECT_VERSION: str = "1.0.0"
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # AI/LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Alpha Vantage Configuration (Market Data)
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
