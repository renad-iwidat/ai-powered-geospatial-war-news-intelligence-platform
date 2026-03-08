"""
GeoNews AI - Interactive War Intelligence Platform
Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import db_manager
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.services.scheduler import start_scheduler, stop_scheduler

# Setup logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="""
    GeoNews AI is an interactive war intelligence platform that transforms news into 
    geographic visualizations and statistical insights using AI.
    
    ## Features
    
    * **News Articles**: Manage and search news articles from multiple sources
    * **Geographic Locations**: Track locations mentioned in news with coordinates
    * **News Events**: Link news articles to geographic locations
    * **Event Metrics**: Extract and analyze numerical data (casualties, weapons, etc)
    * **Analytics**: Comprehensive statistics and timeline views
    * **Data Processing**: Automated NER and metrics extraction
    
    ## Technology Stack
    
    * **NLP**: CAMeL Tools with AraBERT (88.4% F1-score for Arabic NER)
    * **Geocoding**: geopy with Nominatim (OpenStreetMap)
    * **Database**: PostgreSQL with asyncpg
    * **Framework**: FastAPI with Pydantic validation
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
print(f"🔐 CORS Origins: {settings.CORS_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Lifecycle Events
@app.on_event("startup")
async def startup_event():
    """Initialize resources on application startup"""
    await db_manager.connect()
    
    # Start background scheduler
    try:
        import os
        api_base_url = os.getenv("API_BASE_URL", "http://localhost:7235")
        start_scheduler(api_base_url=api_base_url)
    except Exception as e:
        print(f"⚠️  Failed to start scheduler: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on application shutdown"""
    await db_manager.disconnect()
    
    # Stop background scheduler
    try:
        stop_scheduler()
    except Exception as e:
        print(f"⚠️  Failed to stop scheduler: {str(e)}")


# Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns the application status and database connectivity
    """
    try:
        pool = db_manager.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.PROJECT_VERSION
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


# Root Endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Welcome to GeoNews AI API",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }
