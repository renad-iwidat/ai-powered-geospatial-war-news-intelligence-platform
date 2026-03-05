"""
News Event Schemas
Pydantic models for news events
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NewsEventBase(BaseModel):
    """Base schema for news event"""
    raw_news_id: int = Field(..., description="News article ID")
    location_id: int = Field(..., description="Location ID")
    place_name: str = Field(..., description="Place name mentioned in article")
    event_type: Optional[str] = Field(None, description="Event type")


class NewsEventListItem(BaseModel):
    """News event in list view"""
    id: int = Field(..., description="Event ID")
    raw_news_id: int = Field(..., description="News article ID")
    location_id: int = Field(..., description="Location ID")
    place_name: str = Field(..., description="Place name")
    event_type: Optional[str] = Field(None, description="Event type")
    location_name: Optional[str] = Field(None, description="Location name")
    country_code: Optional[str] = Field(None, description="Country code")
    news_title: Optional[str] = Field(None, description="News article title")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    metrics_count: int = Field(0, description="Number of metrics")
    
    class Config:
        from_attributes = True


class NewsEventDetail(BaseModel):
    """Detailed news event"""
    id: int = Field(..., description="Event ID")
    raw_news_id: int = Field(..., description="News article ID")
    location_id: int = Field(..., description="Location ID")
    place_name: str = Field(..., description="Place name")
    event_type: Optional[str] = Field(None, description="Event type")
    created_at: Optional[datetime] = Field(None, description="Creation date")
    
    class Config:
        from_attributes = True


class NewsEventListResponse(BaseModel):
    """Response for news events list"""
    items: List[NewsEventListItem] = Field(..., description="List of events")
    total: int = Field(..., description="Total count")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Offset")
    
    class Config:
        from_attributes = True
