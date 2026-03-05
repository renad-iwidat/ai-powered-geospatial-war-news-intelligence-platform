"""
Geographic Locations Endpoints
API endpoints for managing geographic locations
"""

from fastapi import APIRouter, Query, HTTPException, Depends
import asyncpg

from app.core.database import get_db_pool
from app.schemas import (
    GeographicLocationListResponse,
    GeographicLocationDetail,
    GeographicLocationListItem
)

router = APIRouter()


@router.get("", response_model=GeographicLocationListResponse)
async def get_geographic_locations_list(
    limit: int = Query(100, ge=1, le=500, description="Number of items"),
    country_code: str = Query(None, description="Filter by country code"),
    min_events: int = Query(None, ge=0, description="Minimum number of events"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get list of geographic locations with filters
    
    - **limit**: Number of items (1-500)
    - **country_code**: Filter by country code (e.g., SY, IQ, IR)
    - **min_events**: Minimum number of events at location
    """
    
    # Build WHERE clause
    where_clauses = []
    params = []
    param_idx = 1
    
    if country_code:
        where_clauses.append(f"l.country_code = ${param_idx}")
        params.append(country_code.upper())
        param_idx += 1
    
    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # Query with events count
    query = f"""
        SELECT
            l.id,
            l.name,
            l.country_code,
            l.latitude,
            l.longitude,
            COUNT(ne.id) as events_count
        FROM locations l
        LEFT JOIN news_events ne ON l.id = ne.location_id
        {where_sql}
        GROUP BY l.id, l.name, l.country_code, l.latitude, l.longitude
        {"HAVING COUNT(ne.id) >= $" + str(param_idx) if min_events is not None else ""}
        ORDER BY events_count DESC, l.name
        LIMIT ${param_idx + (1 if min_events is not None else 0)}
    """
    
    if min_events is not None:
        params.append(min_events)
        param_idx += 1
    params.append(limit)
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
    
    items = [GeographicLocationListItem(**dict(row)) for row in rows]
    
    return GeographicLocationListResponse(
        items=items,
        total=len(items)
    )


@router.get("/{location_id}", response_model=GeographicLocationDetail)
async def get_geographic_location_detail(
    location_id: int,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get detailed information about a specific geographic location
    
    - **location_id**: The ID of the location
    """
    
    query = """
        SELECT
            id,
            name,
            country_code,
            latitude,
            longitude,
            region_level,
            osm_id,
            osm_type
        FROM locations
        WHERE id = $1
        LIMIT 1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, location_id)
    
    if not row:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return GeographicLocationDetail(**dict(row))



@router.get("/{location_id}/events")
async def get_location_events(
    location_id: int,
    limit: int = Query(50, ge=1, le=200, description="Number of items"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get all events at a specific location
    
    - **location_id**: The ID of the location
    - **limit**: Number of items per page
    - **offset**: Offset for pagination
    """
    
    # Get total count
    count_query = """
        SELECT COUNT(*)
        FROM news_events ne
        WHERE ne.location_id = $1
    """
    
    # Get events
    events_query = """
        SELECT
            ne.id,
            ne.raw_news_id,
            ne.place_name,
            ne.event_type,
            rn.title_original as news_title,
            rn.published_at,
            (SELECT COUNT(*) FROM event_metrics em WHERE em.event_id = ne.id) as metrics_count
        FROM news_events ne
        LEFT JOIN raw_news rn ON ne.raw_news_id = rn.id
        WHERE ne.location_id = $1
        ORDER BY rn.published_at DESC NULLS LAST
        LIMIT $2 OFFSET $3
    """
    
    async with pool.acquire() as conn:
        total = await conn.fetchval(count_query, location_id)
        rows = await conn.fetch(events_query, location_id, limit, offset)
    
    return {
        "events": [dict(row) for row in rows],
        "total": total,
        "limit": limit,
        "offset": offset
    }
