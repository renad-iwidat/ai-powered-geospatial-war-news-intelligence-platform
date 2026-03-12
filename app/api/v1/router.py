"""
API v1 Router
Main router combining all v1 endpoints with clear organization
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    news_articles,
    geographic_locations,
    news_events,
    event_metrics,
    analytics_statistics,
    data_processing,
    predictions,
    market_data,
    sources
)

# Create main API router
api_router = APIRouter()

# News Articles Endpoints
api_router.include_router(
    news_articles.router,
    prefix="/news-articles",
    tags=["News Articles"],
    responses={404: {"description": "Not found"}}
)

# Geographic Locations Endpoints
api_router.include_router(
    geographic_locations.router,
    prefix="/geographic-locations",
    tags=["Geographic Locations"],
    responses={404: {"description": "Not found"}}
)

# News Events Endpoints
api_router.include_router(
    news_events.router,
    prefix="/news-events",
    tags=["News Events"],
    responses={404: {"description": "Not found"}}
)

# Event Metrics Endpoints
api_router.include_router(
    event_metrics.router,
    prefix="/event-metrics",
    tags=["Event Metrics"],
    responses={404: {"description": "Not found"}}
)

# Analytics & Statistics Endpoints
api_router.include_router(
    analytics_statistics.router,
    prefix="/analytics",
    tags=["Analytics & Statistics"],
    responses={404: {"description": "Not found"}}
)

# Data Processing Endpoints
api_router.include_router(
    data_processing.router,
    prefix="/data-processing",
    tags=["Data Processing"],
    responses={404: {"description": "Not found"}}
)

# Predictions & Forecasting Endpoints
api_router.include_router(
    predictions.router,
    prefix="/predictions",
    tags=["Predictions & Forecasting"],
    responses={404: {"description": "Not found"}}
)

# Market Data Endpoints
api_router.include_router(
    market_data.router,
    prefix="/market-data",
    tags=["Market Data"],
    responses={404: {"description": "Not found"}}
)

# Sources Endpoints
api_router.include_router(
    sources.router,
    prefix="/sources",
    tags=["Sources"],
    responses={404: {"description": "Not found"}}
)
