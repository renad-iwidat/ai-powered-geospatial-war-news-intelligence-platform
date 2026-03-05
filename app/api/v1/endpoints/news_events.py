"""
News Events Endpoints
API endpoints for managing news events
"""

from fastapi import APIRouter, Query, HTTPException, Depends
import asyncpg

from app.core.database import get_db_pool
from app.schemas import (
    NewsEventListResponse,
    NewsEventDetail,
    NewsEventListItem
)

router = APIRouter()


@router.get("", response_model=NewsEventListResponse)
async def get_news_events_list(
    limit: int = Query(50, ge=1, le=200, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    country_code: str = Query(None, description="Filter by country code"),
    event_type: str = Query(None, description="Filter by event type"),
    has_metrics: bool = Query(None, description="Filter by metrics existence"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get list of news events with pagination and filters
    
    - **limit**: Number of items per page (1-200)
    - **offset**: Offset for pagination
    - **country_code**: Filter by country code
    - **event_type**: Filter by event type
    - **has_metrics**: Filter events with/without metrics
    """
    
    # Build WHERE clause
    where_clauses = []
    params = []
    param_idx = 1
    
    if country_code:
        where_clauses.append(f"l.country_code = ${param_idx}")
        params.append(country_code.upper())
        param_idx += 1
    
    if event_type:
        where_clauses.append(f"ne.event_type = ${param_idx}")
        params.append(event_type)
        param_idx += 1
    
    if has_metrics is not None:
        if has_metrics:
            where_clauses.append("metrics_count > 0")
        else:
            where_clauses.append("metrics_count = 0")
    
    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # Get total count
    count_query = f"""
        SELECT COUNT(*)
        FROM news_events ne
        LEFT JOIN locations l ON ne.location_id = l.id
        LEFT JOIN (
            SELECT event_id, COUNT(*) as metrics_count
            FROM event_metrics
            GROUP BY event_id
        ) em ON ne.id = em.event_id
        {where_sql}
    """
    
    # Get paginated list
    list_query = f"""
        SELECT
            ne.id,
            ne.raw_news_id,
            ne.location_id,
            ne.place_name,
            ne.event_type,
            l.name as location_name,
            l.country_code,
            rn.title_original as news_title,
            rn.published_at,
            COALESCE(em.metrics_count, 0) as metrics_count
        FROM news_events ne
        LEFT JOIN locations l ON ne.location_id = l.id
        LEFT JOIN raw_news rn ON ne.raw_news_id = rn.id
        LEFT JOIN (
            SELECT event_id, COUNT(*) as metrics_count
            FROM event_metrics
            GROUP BY event_id
        ) em ON ne.id = em.event_id
        {where_sql}
        ORDER BY rn.published_at DESC NULLS LAST
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
    """
    params.extend([limit, offset])
    
    async with pool.acquire() as conn:
        total = await conn.fetchval(count_query, *params[:-2]) if params[:-2] else await conn.fetchval(count_query)
        rows = await conn.fetch(list_query, *params)
    
    items = [NewsEventListItem(**dict(row)) for row in rows]
    
    return NewsEventListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )



@router.get("/{event_id}", response_model=NewsEventDetail)
async def get_news_event_detail(
    event_id: int,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get detailed information about a specific news event
    
    - **event_id**: The ID of the event
    """
    
    query = """
        SELECT
            id,
            raw_news_id,
            location_id,
            place_name,
            event_type,
            created_at
        FROM news_events
        WHERE id = $1
        LIMIT 1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, event_id)
    
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return NewsEventDetail(**dict(row))
