"""
Data Processing Schemas
Pydantic models for data processing operations
"""

from pydantic import BaseModel, Field
from typing import Optional


class LocationExtractionRequest(BaseModel):
    """Request for location extraction"""
    batch_size: int = Field(20, ge=1, le=100, description="Number of articles to process")


class LocationExtractionResponse(BaseModel):
    """Response for location extraction"""
    processed_news: int = Field(..., description="Number of articles processed")
    places_detected: int = Field(..., description="Number of places detected")
    locations_upserted: int = Field(..., description="Number of locations stored")
    events_created: int = Field(..., description="Number of events created")
    
    class Config:
        from_attributes = True


class MetricsExtractionRequest(BaseModel):
    """Request for metrics extraction"""
    batch_size: int = Field(50, ge=1, le=200, description="Number of events to process")


class MetricsExtractionResponse(BaseModel):
    """Response for metrics extraction"""
    events_processed: int = Field(..., description="Number of events processed")
    metrics_extracted: int = Field(..., description="Number of metrics extracted")
    
    class Config:
        from_attributes = True


class ProcessingStatus(BaseModel):
    """Processing status"""
    total_articles: int = Field(..., description="Total number of articles")
    articles_with_events: int = Field(..., description="Articles with events")
    articles_without_events: int = Field(..., description="Articles without events")
    total_events: int = Field(..., description="Total number of events")
    events_with_metrics: int = Field(..., description="Events with metrics")
    events_without_metrics: int = Field(..., description="Events without metrics")
    processing_completion_percentage: float = Field(..., description="Processing completion percentage")
    
    class Config:
        from_attributes = True
