"""
Event Metric Schemas
Pydantic models for event metrics
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class EventMetricBase(BaseModel):
    """Base schema for event metric"""
    event_id: int = Field(..., description="Event ID")
    metric_type: str = Field(..., description="Metric type (missiles_launched, casualties, etc)")
    value: int = Field(..., description="Metric value")
    snippet: Optional[str] = Field(None, description="Text snippet where metric was found")


class EventMetricListItem(BaseModel):
    """Event metric in list view"""
    id: int = Field(..., description="Metric ID")
    event_id: int = Field(..., description="Event ID")
    metric_type: str = Field(..., description="Metric type")
    value: int = Field(..., description="Metric value")
    snippet: Optional[str] = Field(None, description="Text snippet")
    location_name: Optional[str] = Field(None, description="Location name")
    country_code: Optional[str] = Field(None, description="Country code")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    
    class Config:
        from_attributes = True


class EventMetricSummary(BaseModel):
    """Summary of metrics by type"""
    metric_type: str = Field(..., description="Metric type")
    total_count: int = Field(..., description="Number of occurrences")
    total_value: int = Field(..., description="Sum of all values")
    avg_value: float = Field(..., description="Average value")
    min_value: int = Field(..., description="Minimum value")
    max_value: int = Field(..., description="Maximum value")
    
    class Config:
        from_attributes = True


class EventMetricListResponse(BaseModel):
    """Response for event metrics list"""
    items: List[EventMetricListItem] = Field(..., description="List of metrics")
    total: int = Field(..., description="Total count")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Offset")
    
    class Config:
        from_attributes = True


class EventMetricSummaryResponse(BaseModel):
    """Response for metrics summary"""
    summary_by_type: List[EventMetricSummary] = Field(..., description="Summary grouped by metric type")
    total_metrics: int = Field(..., description="Total number of metrics")
    
    class Config:
        from_attributes = True
