"""
Event Metrics Endpoints
API endpoints for managing event metrics
"""

from fastapi import APIRouter, Query, Depends
import asyncpg

from app.core.database import get_db_pool
from app.schemas import (
    EventMetricListResponse,
    EventMetricSummaryResponse,
    EventMetricListItem,
    EventMetricSummary
)

router = APIRouter()


@router.get("", response_model=EventMetricListResponse)
async def get_event_metrics_list(
    limit: int = Query(50, ge=1, le=200, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    metric_type: str = Query(None, description="Filter by metric type"),
    country_code: str = Query(None, description="Filter by country code"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get list of event metrics with pagination and filters
    
    - **limit**: Number of items per page (1-200)
    - **offset**: Offset for pagination
    - **metric_type**: Filter by metric type (missiles_launched, casualties, etc)
    - **country_code**: Filter by country code
    """
    
    # Build WHERE clause
    where_clauses = []
    params = []
    param_idx = 1
    
    if metric_type:
        where_clauses.append(f"em.metric_type = ${param_idx}")
        params.append(metric_type)
        param_idx += 1
    
    if country_code:
        where_clauses.append(f"l.country_code = ${param_idx}")
        params.append(country_code.upper())
        param_idx += 1
    
    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # Get total count
    count_query = f"""
        SELECT COUNT(*)
        FROM event_metrics em
        JOIN news_events ne ON em.event_id = ne.id
        LEFT JOIN locations l ON ne.location_id = l.id
        {where_sql}
    """
    
    # Get paginated list
    list_query = f"""
        SELECT
            em.id,
            em.event_id,
            em.metric_type,
            em.value,
            em.snippet,
            l.name as location_name,
            l.country_code,
            rn.published_at
        FROM event_metrics em
        JOIN news_events ne ON em.event_id = ne.id
        LEFT JOIN locations l ON ne.location_id = l.id
        LEFT JOIN raw_news rn ON ne.raw_news_id = rn.id
        {where_sql}
        ORDER BY rn.published_at DESC NULLS LAST, em.value DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
    """
    params.extend([limit, offset])
    
    async with pool.acquire() as conn:
        total = await conn.fetchval(count_query, *params[:-2]) if params[:-2] else await conn.fetchval(count_query)
        rows = await conn.fetch(list_query, *params)
    
    items = [EventMetricListItem(**dict(row)) for row in rows]
    
    return EventMetricListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )



@router.get("/summary", response_model=EventMetricSummaryResponse)
async def get_event_metrics_summary(
    country_code: str = Query(None, description="Filter by country code"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get summary of metrics grouped by type
    
    - **country_code**: Filter by country code (optional)
    """
    
    # Build WHERE clause
    where_sql = ""
    params = []
    
    if country_code:
        where_sql = "WHERE l.country_code = $1"
        params.append(country_code.upper())
    
    query = f"""
        SELECT
            em.metric_type,
            COUNT(*) as total_count,
            SUM(em.value) as total_value,
            AVG(em.value)::float as avg_value,
            MIN(em.value) as min_value,
            MAX(em.value) as max_value
        FROM event_metrics em
        JOIN news_events ne ON em.event_id = ne.id
        LEFT JOIN locations l ON ne.location_id = l.id
        {where_sql}
        GROUP BY em.metric_type
        ORDER BY total_value DESC
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        total_metrics = await conn.fetchval(
            f"SELECT COUNT(*) FROM event_metrics em JOIN news_events ne ON em.event_id = ne.id LEFT JOIN locations l ON ne.location_id = l.id {where_sql}",
            *params
        )
    
    summary = [EventMetricSummary(**dict(row)) for row in rows]
    
    return EventMetricSummaryResponse(
        summary_by_type=summary,
        total_metrics=total_metrics
    )
