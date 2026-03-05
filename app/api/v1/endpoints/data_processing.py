"""
Data Processing Endpoints
API endpoints for triggering data processing operations
"""

from fastapi import APIRouter, Depends, Body
import asyncpg

from app.core.database import get_db_pool
from app.schemas import (
    LocationExtractionRequest,
    LocationExtractionResponse,
    MetricsExtractionRequest,
    MetricsExtractionResponse,
    ProcessingStatus
)
from app.services.geo.location_processor import process_locations
from app.services.extraction.metrics_processor import process_metrics

router = APIRouter()


@router.post("/extract-locations", response_model=LocationExtractionResponse)
async def extract_locations_from_news(
    request: LocationExtractionRequest = Body(...),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Extract geographic locations from news articles
    
    - **batch_size**: Number of articles to process (1-100)
    
    This endpoint:
    1. Reads unprocessed Arabic news articles
    2. Extracts place names using CAMeL Tools NER
    3. Converts place names to coordinates using geopy
    4. Stores locations and creates events
    """
    
    result = await process_locations(pool, batch_size=request.batch_size)
    return LocationExtractionResponse(**result)


@router.post("/extract-metrics", response_model=MetricsExtractionResponse)
async def extract_metrics_from_events(
    request: MetricsExtractionRequest = Body(...),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Extract numerical metrics from news events
    
    - **batch_size**: Number of events to process (1-200)
    
    This endpoint:
    1. Reads events without metrics
    2. Extracts numerical data (missiles, casualties, etc)
    3. Stores metrics in database
    """
    
    result = await process_metrics(pool, batch_size=request.batch_size)
    return MetricsExtractionResponse(**result)



@router.get("/status", response_model=ProcessingStatus)
async def get_processing_status(
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get current processing status
    
    Returns statistics about processing completion:
    - Total articles and how many have events
    - Total events and how many have metrics
    - Overall processing completion percentage
    """
    
    async with pool.acquire() as conn:
        # Articles stats
        total_articles = await conn.fetchval("SELECT COUNT(*) FROM raw_news")
        articles_with_events = await conn.fetchval(
            "SELECT COUNT(DISTINCT raw_news_id) FROM news_events"
        )
        articles_without_events = total_articles - articles_with_events
        
        # Events stats
        total_events = await conn.fetchval("SELECT COUNT(*) FROM news_events")
        events_with_metrics = await conn.fetchval(
            "SELECT COUNT(DISTINCT event_id) FROM event_metrics"
        )
        events_without_metrics = total_events - events_with_metrics
        
        # Calculate completion percentage
        # Weight: 50% for location extraction, 50% for metrics extraction
        location_completion = (articles_with_events / total_articles * 100) if total_articles > 0 else 0
        metrics_completion = (events_with_metrics / total_events * 100) if total_events > 0 else 0
        overall_completion = (location_completion * 0.5 + metrics_completion * 0.5)
    
    return ProcessingStatus(
        total_articles=total_articles,
        articles_with_events=articles_with_events,
        articles_without_events=articles_without_events,
        total_events=total_events,
        events_with_metrics=events_with_metrics,
        events_without_metrics=events_without_metrics,
        processing_completion_percentage=round(overall_completion, 2)
    )
