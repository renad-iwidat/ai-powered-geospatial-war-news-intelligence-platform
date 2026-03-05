"""
Analytics Schemas
Pydantic models for analytics and statistics
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date as DateType


class AnalyticsOverview(BaseModel):
    """Overview analytics"""
    total_news_articles: int = Field(..., description="Total number of news articles")
    total_locations: int = Field(..., description="Total number of locations")
    total_events: int = Field(..., description="Total number of events")
    total_metrics: int = Field(..., description="Total number of metrics")
    total_countries: int = Field(..., description="Number of countries mentioned")
    articles_with_events: int = Field(..., description="Articles that have events")
    articles_without_events: int = Field(..., description="Articles without events")
    events_with_metrics: int = Field(..., description="Events that have metrics")
    events_without_metrics: int = Field(..., description="Events without metrics")
    
    class Config:
        from_attributes = True


class CountryStatistics(BaseModel):
    """Statistics by country"""
    country_code: str = Field(..., description="Country code")
    country_name: Optional[str] = Field(None, description="Country name")
    locations_count: int = Field(..., description="Number of locations")
    events_count: int = Field(..., description="Number of events")
    metrics_count: int = Field(..., description="Number of metrics")
    
    class Config:
        from_attributes = True


class CountryStatisticsResponse(BaseModel):
    """Response for country statistics"""
    countries: List[CountryStatistics] = Field(..., description="Statistics by country")
    total_countries: int = Field(..., description="Total number of countries")
    
    class Config:
        from_attributes = True


class DateStatistics(BaseModel):
    """Statistics by date"""
    date: DateType = Field(..., description="Date")
    articles_count: int = Field(..., description="Number of articles")
    events_count: int = Field(..., description="Number of events")
    metrics_count: int = Field(..., description="Number of metrics")
    
    class Config:
        from_attributes = True


class DateStatisticsResponse(BaseModel):
    """Response for date statistics"""
    daily_stats: List[DateStatistics] = Field(..., description="Daily statistics")
    date_range_start: DateType = Field(..., description="Start date")
    date_range_end: DateType = Field(..., description="End date")
    
    class Config:
        from_attributes = True


class TimelineItem(BaseModel):
    """Timeline item"""
    date: DateType = Field(..., description="Date")
    event_id: int = Field(..., description="Event ID")
    location_name: str = Field(..., description="Location name")
    country_code: str = Field(..., description="Country code")
    news_title: str = Field(..., description="News title")
    metrics: Dict[str, int] = Field(default_factory=dict, description="Metrics for this event")
    
    class Config:
        from_attributes = True


class TimelineResponse(BaseModel):
    """Response for timeline"""
    timeline: List[TimelineItem] = Field(..., description="Timeline items")
    total_items: int = Field(..., description="Total number of items")
    
    class Config:
        from_attributes = True
