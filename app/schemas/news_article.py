"""
News Article Schemas
Pydantic models for news articles
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NewsArticleBase(BaseModel):
    """Base schema for news article"""
    title: str = Field(..., description="Article title")
    content: Optional[str] = Field(None, description="Article content")
    url: str = Field(..., description="Article URL")
    published_at: Optional[datetime] = Field(None, description="Publication date")


class NewsArticleListItem(BaseModel):
    """News article in list view"""
    id: int = Field(..., description="Article ID")
    title: str = Field(..., description="Article title")
    content_preview: Optional[str] = Field(None, description="Content preview (first 200 chars)")
    url: str = Field(..., description="Article URL")
    source_name: Optional[str] = Field(None, description="Source name")
    language_code: str = Field(..., description="Language code (ar, en, he)")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    has_numbers: bool = Field(False, description="Contains numerical data")
    events_count: int = Field(0, description="Number of events")
    metrics_count: int = Field(0, description="Number of metrics")
    
    class Config:
        from_attributes = True


class NewsArticleDetail(BaseModel):
    """Detailed news article"""
    id: int = Field(..., description="Article ID")
    title: str = Field(..., description="Article title")
    content: Optional[str] = Field(None, description="Full article content")
    url: str = Field(..., description="Article URL")
    source_name: Optional[str] = Field(None, description="Source name")
    language_code: str = Field(..., description="Language code")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    fetched_at: Optional[datetime] = Field(None, description="Fetch date")
    has_numbers: bool = Field(False, description="Contains numerical data")
    
    class Config:
        from_attributes = True


class NewsArticleListResponse(BaseModel):
    """Response for news articles list"""
    items: List[NewsArticleListItem] = Field(..., description="List of articles")
    total: int = Field(..., description="Total count")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Offset")
    
    class Config:
        from_attributes = True
