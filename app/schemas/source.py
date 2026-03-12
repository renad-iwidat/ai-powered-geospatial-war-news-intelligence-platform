"""
Source Schemas
Pydantic models for news sources
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SourceBase(BaseModel):
    """Base schema for source"""
    name: str = Field(..., description="Source name")
    url: str = Field(..., description="Source URL")
    is_active: bool = Field(..., description="Is source active")


class SourceDetail(BaseModel):
    """Detailed source information"""
    id: int = Field(..., description="Source ID")
    name: str = Field(..., description="Source name")
    url: str = Field(..., description="Source URL")
    is_active: bool = Field(..., description="Is source active")
    source_type_id: int = Field(..., description="Source type ID")
    source_type_name: Optional[str] = Field(None, description="Source type name")
    created_at: Optional[datetime] = Field(None, description="Creation date")
    articles_count: int = Field(0, description="Number of articles from this source")
    
    class Config:
        from_attributes = True


class SourceListItem(BaseModel):
    """Source in list view"""
    id: int = Field(..., description="Source ID")
    name: str = Field(..., description="Source name")
    url: str = Field(..., description="Source URL")
    is_active: bool = Field(..., description="Is source active")
    source_type_id: int = Field(..., description="Source type ID")
    source_type_name: Optional[str] = Field(None, description="Source type name")
    articles_count: int = Field(0, description="Number of articles from this source")
    
    class Config:
        from_attributes = True


class SourceListResponse(BaseModel):
    """Response for sources list"""
    items: List[SourceListItem] = Field(..., description="List of sources")
    total: int = Field(..., description="Total count")
    active_count: int = Field(..., description="Number of active sources")
    inactive_count: int = Field(..., description="Number of inactive sources")
    
    class Config:
        from_attributes = True


class SourceStatusResponse(BaseModel):
    """Response for source status"""
    id: int = Field(..., description="Source ID")
    name: str = Field(..., description="Source name")
    is_active: bool = Field(..., description="Is source active")
    status: str = Field(..., description="Status text (Active/Inactive)")
    articles_count: int = Field(0, description="Number of articles from this source")
    
    class Config:
        from_attributes = True
