"""
Core Configuration Module
Centralized configuration management using Pydantic Settings
"""

import os
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
    
    # CORS - Can be JSON array or comma-separated string
    CORS_ORIGINS_STR: str = "http://localhost:3001"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # AI/LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Alpha Vantage Configuration (Market Data)
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    
    # Docker Configuration (optional, for docker-compose)
    BACKEND_PORT: Optional[str] = None
    FRONTEND_PORT: Optional[str] = None
    API_BASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env
    
    @property
    def CORS_ORIGINS(self) -> list[str]:
        """Parse CORS_ORIGINS from JSON array or comma-separated string"""
        import json
        origins_str = self.CORS_ORIGINS_STR.strip()
        
        # Try to parse as JSON array first
        if origins_str.startswith('['):
            try:
                return json.loads(origins_str)
            except json.JSONDecodeError:
                pass
        
        # Fall back to comma-separated parsing
        return [origin.strip() for origin in origins_str.split(",")]


# Global settings instance
settings = Settings()
