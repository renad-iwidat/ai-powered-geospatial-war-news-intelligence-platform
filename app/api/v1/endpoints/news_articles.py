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
    NewsArticleListItem,
    NewsArticleBySource,
    NewsArticlesBySourceResponse
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
    count_query = f"SELECT COUNT(*) FROM raw_news rn LEFT JOIN translations t ON rn.id = t.raw_news_id AND t.language_id = 1 WHERE (rn.language_id = 1 OR t.language_id = 1)"
    
    # Get paginated list
    list_query = f"""
        SELECT
            rn.id,
            CASE 
                WHEN rn.language_id = 1 THEN rn.title_original
                ELSE COALESCE(t.title, rn.title_original)
            END AS title,
            CASE 
                WHEN rn.language_id = 1 THEN LEFT(rn.content_original, 200)
                ELSE LEFT(COALESCE(t.content, rn.content_original), 200)
            END AS content_preview,
            CASE 
                WHEN rn.language_id = 1 THEN rn.content_original
                ELSE COALESCE(t.content, rn.content_original)
            END AS content,
            rn.url,
            s.name as source_name,
            'ar' as language_code,
            COALESCE(rn.published_at, rn.fetched_at) as published_at,
            (SELECT COUNT(*) FROM news_events ne WHERE ne.raw_news_id = rn.id) as events_count,
            (SELECT COUNT(*) FROM event_metrics em 
             JOIN news_events ne ON em.event_id = ne.id 
             WHERE ne.raw_news_id = rn.id) as metrics_count,
            false as has_numbers
        FROM raw_news rn
        LEFT JOIN translations t ON rn.id = t.raw_news_id AND t.language_id = 1
        LEFT JOIN sources s ON rn.source_id = s.id
        WHERE (rn.language_id = 1 OR t.language_id = 1)
        ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC NULLS LAST
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


@router.get("/by-source/{source_id}", response_model=NewsArticlesBySourceResponse)
async def get_news_articles_by_source(
    source_id: int,
    limit: int = Query(50, ge=1, le=200, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    search: str = Query(None, description="Search in title or content"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get all news articles from a specific source with all details
    
    Returns articles from both raw_news and translations tables
    
    - **source_id**: The ID of the news source
    - **limit**: Number of items per page (1-200)
    - **offset**: Offset for pagination
    - **search**: Optional search query for title or content
    """
    
    # Build WHERE clause
    where_clauses = ["rn.source_id = $1"]
    params = [source_id]
    param_idx = 2
    
    if search:
        where_clauses.append(f"(rn.title_original ILIKE ${param_idx} OR rn.content_original ILIKE ${param_idx} OR t.title ILIKE ${param_idx} OR t.content ILIKE ${param_idx})")
        params.append(f"%{search}%")
        param_idx += 1
    
    where_sql = " AND ".join(where_clauses)
    
    # Get total count
    count_query = f"""
        SELECT COUNT(*)
        FROM (
            SELECT DISTINCT rn.id
            FROM raw_news rn
            LEFT JOIN translations t ON rn.id = t.raw_news_id
            WHERE {where_sql}
        ) as distinct_articles
    """
    
    # Get paginated list with all details from both raw_news and translations
    list_query = f"""
        SELECT
            rn.id,
            CASE 
                WHEN rn.language_id = 1 THEN rn.title_original
                ELSE COALESCE(t.title, rn.title_original)
            END AS title,
            CASE 
                WHEN rn.language_id = 1 THEN rn.content_original
                ELSE COALESCE(t.content, rn.content_original)
            END AS content,
            rn.url,
            s.name as source_name,
            s.id as source_id,
            CASE 
                WHEN rn.language_id = 1 THEN 'ar'
                WHEN t.language_id = 2 THEN 'en'
                WHEN t.language_id = 3 THEN 'he'
                ELSE 'ar'
            END as language_code,
            rn.published_at,
            rn.fetched_at
        FROM raw_news rn
        LEFT JOIN translations t ON rn.id = t.raw_news_id
        LEFT JOIN sources s ON rn.source_id = s.id
        WHERE {where_sql}
        ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC NULLS LAST
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
    """
    params.extend([limit, offset])
    
    # Get source name
    source_query = "SELECT name FROM sources WHERE id = $1"
    
    async with pool.acquire() as conn:
        total = await conn.fetchval(count_query, *params[:-2]) if len(params) > 3 else await conn.fetchval(count_query, source_id)
        rows = await conn.fetch(list_query, *params)
        source_row = await conn.fetchrow(source_query, source_id)
    
    source_name = source_row['name'] if source_row else None
    
    items = [NewsArticleBySource(**dict(row)) for row in rows]
    
    return NewsArticlesBySourceResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        source_id=source_id,
        source_name=source_name
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
            rn.id,
            CASE 
                WHEN rn.language_id = 1 THEN rn.title_original
                ELSE COALESCE(t.title, rn.title_original)
            END AS title,
            CASE 
                WHEN rn.language_id = 1 THEN rn.content_original
                ELSE COALESCE(t.content, rn.content_original)
            END AS content,
            rn.url,
            s.name as source_name,
            'ar' as language_code,
            rn.published_at,
            rn.fetched_at
        FROM raw_news rn
        LEFT JOIN translations t ON rn.id = t.raw_news_id AND t.language_id = 1
        LEFT JOIN sources s ON rn.source_id = s.id
        WHERE rn.id = $1
        AND (rn.language_id = 1 OR t.language_id = 1)
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
