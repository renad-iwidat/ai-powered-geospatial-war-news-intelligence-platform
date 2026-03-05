"""
Geographic Location Schemas
Pydantic models for geographic locations
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class GeographicLocationBase(BaseModel):
    """Base schema for geographic location"""
    name: str = Field(..., description="Location name")
    country_code: str = Field(..., description="Country code (ISO 3166-1 alpha-2)")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")


class GeographicLocationListItem(BaseModel):
    """Geographic location in list view"""
    id: int = Field(..., description="Location ID")
    name: str = Field(..., description="Location name")
    country_code: str = Field(..., description="Country code")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    events_count: int = Field(0, description="Number of events at this location")
    
    class Config:
        from_attributes = True


class GeographicLocationDetail(BaseModel):
    """Detailed geographic location"""
    id: int = Field(..., description="Location ID")
    name: str = Field(..., description="Location name")
    country_code: str = Field(..., description="Country code")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    region_level: Optional[str] = Field(None, description="Region level (city, country, etc)")
    osm_id: Optional[int] = Field(None, description="OpenStreetMap ID")
    osm_type: Optional[str] = Field(None, description="OpenStreetMap type")
    
    class Config:
        from_attributes = True


class GeographicLocationListResponse(BaseModel):
    """Response for geographic locations list"""
    items: List[GeographicLocationListItem] = Field(..., description="List of locations")
    total: int = Field(..., description="Total count")
    
    class Config:
        from_attributes = True
