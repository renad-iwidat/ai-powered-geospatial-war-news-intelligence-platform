"""
News Articles Endpoints
API endpoints for managing news articles
"""

from fastapi import APIRouter, Query, HTTPException, Depends
import asyncpg

from app.core.database import get_db_pool
from app.schemas import (
    NewsArticleListResponse,
    NewsArticleDetail,
    NewsArticleListItem
)

router = APIRouter()


@router.get("", response_model=NewsArticleListResponse)
async def get_news_articles_list(
    limit: int = Query(50, ge=1, le=200, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    search: str = Query(None, description="Search in title or content"),
    language: str = Query(None, description="Filter by language code (ar, en, he)"),
    has_events: bool = Query(None, description="Filter by events existence"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get list of news articles with pagination and filters
    
    - **limit**: Number of items per page (1-200)
    - **offset**: Offset for pagination
    - **search**: Search query for title or content
    - **language**: Filter by language code
    - **has_events**: Filter articles with/without events
    """
    
    # Build WHERE clause
    where_clauses = []
    params = []
    param_idx = 1
    
    if search:
        where_clauses.append(f"(title_ar ILIKE ${param_idx} OR content_ar ILIKE ${param_idx})")
        params.append(f"%{search}%")
        param_idx += 1
    
    if language:
        where_clauses.append(f"language_code = ${param_idx}")
        params.append(language)
        param_idx += 1
    
    if has_events is not None:
        if has_events:
            where_clauses.append("events_count > 0")
        else:
            where_clauses.append("events_count = 0")
    
    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM vw_news_ar_feed {where_sql}"
    
    # Get paginated list
    list_query = f"""
        SELECT
            raw_news_id as id,
            title_ar as title,
            LEFT(content_ar, 200) as content_preview,
            url,
            source_mode as source_name,
            'ar' as language_code,
            COALESCE(published_at, fetched_at) as published_at,
            has_numbers,
            events_count,
            metrics_count
        FROM vw_news_ar_feed
        {where_sql}
        ORDER BY COALESCE(published_at, fetched_at) DESC NULLS LAST
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
    """
    params.extend([limit, offset])
    
    async with pool.acquire() as conn:
        total = await conn.fetchval(count_query, *params[:-2]) if params[:-2] else await conn.fetchval(count_query)
        rows = await conn.fetch(list_query, *params)
    
    items = [NewsArticleListItem(**dict(row)) for row in rows]
    
    return NewsArticleListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )



@router.get("/{article_id}", response_model=NewsArticleDetail)
async def get_news_article_detail(
    article_id: int,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get detailed information about a specific news article
    
    - **article_id**: The ID of the news article
    """
    
    query = """
        SELECT
            raw_news_id as id,
            title_ar as title,
            content_ar as content,
            url,
            source_mode as source_name,
            'ar' as language_code,
            published_at,
            fetched_at,
            has_numbers
        FROM vw_news_ar_feed
        WHERE raw_news_id = $1
        LIMIT 1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, article_id)
    
    if not row:
        raise HTTPException(status_code=404, detail="News article not found")
    
    return NewsArticleDetail(**dict(row))


@router.get("/{article_id}/events")
async def get_news_article_events(
    article_id: int,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get all events associated with a news article
    
    - **article_id**: The ID of the news article
    """
    
    query = """
        SELECT
            ne.id,
            ne.place_name,
            ne.event_type,
            l.name as location_name,
            l.country_code,
            l.latitude,
            l.longitude,
            (SELECT COUNT(*) FROM event_metrics em WHERE em.event_id = ne.id) as metrics_count
        FROM news_events ne
        LEFT JOIN locations l ON ne.location_id = l.id
        WHERE ne.raw_news_id = $1
        ORDER BY ne.id
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, article_id)
    
    return {"events": [dict(row) for row in rows], "total": len(rows)}


@router.get("/{article_id}/metrics")
async def get_news_article_metrics(
    article_id: int,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get all metrics associated with a news article
    
    - **article_id**: The ID of the news article
    """
    
    query = """
        SELECT
            em.id,
            em.metric_type,
            em.value,
            em.snippet,
            ne.place_name,
            l.name as location_name,
            l.country_code
        FROM event_metrics em
        JOIN news_events ne ON em.event_id = ne.id
        LEFT JOIN locations l ON ne.location_id = l.id
        WHERE ne.raw_news_id = $1
        ORDER BY em.metric_type, em.value DESC
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, article_id)
    
    return {"metrics": [dict(row) for row in rows], "total": len(rows)}
