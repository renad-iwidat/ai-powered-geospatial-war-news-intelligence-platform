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
    where_clauses = ["(rn.language_id = 1 OR t.id IS NOT NULL)"]
    params = []
    param_idx = 1
    
    if search:
        where_clauses.append(
            f"""(
                CASE
                    WHEN rn.language_id = 1 THEN rn.title_original
                    ELSE t.title
                END ILIKE ${param_idx}
                OR
                CASE
                    WHEN rn.language_id = 1 THEN rn.content_original
                    ELSE t.content
                END ILIKE ${param_idx}
            )"""
        )
        params.append(f"%{search}%")
        param_idx += 1
    
    if language:
        where_clauses.append(f"${param_idx} = 'ar'")
        params.append(language.lower())
        param_idx += 1
    
    if has_events is not None:
        if has_events:
            where_clauses.append(
                "EXISTS (SELECT 1 FROM news_events ne2 WHERE ne2.raw_news_id = rn.id)"
            )
        else:
            where_clauses.append(
                "NOT EXISTS (SELECT 1 FROM news_events ne2 WHERE ne2.raw_news_id = rn.id)"
            )
    
    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # Get total count
    count_query = f"""
        SELECT COUNT(*)
        FROM raw_news rn
        LEFT JOIN LATERAL (
            SELECT tr.id
            FROM translations tr
            WHERE tr.raw_news_id = rn.id
              AND tr.language_id = 1
              AND (
                  NULLIF(BTRIM(COALESCE(tr.title, '')), '') IS NOT NULL
                  OR NULLIF(BTRIM(COALESCE(tr.content, '')), '') IS NOT NULL
              )
            ORDER BY tr.created_at DESC NULLS LAST, tr.id DESC
            LIMIT 1
        ) t ON TRUE
        {where_sql}
    """
    
    # Get paginated list
    list_query = f"""
        SELECT
            rn.id,
            CASE 
                WHEN rn.language_id = 1 THEN rn.title_original
                ELSE t.title
            END AS title,
            CASE 
                WHEN rn.language_id = 1 THEN LEFT(rn.content_original, 200)
                ELSE LEFT(t.content, 200)
            END AS content_preview,
            CASE 
                WHEN rn.language_id = 1 THEN rn.content_original
                ELSE t.content
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
        LEFT JOIN LATERAL (
            SELECT tr.id, tr.title, tr.content
            FROM translations tr
            WHERE tr.raw_news_id = rn.id
              AND tr.language_id = 1
              AND (
                  NULLIF(BTRIM(COALESCE(tr.title, '')), '') IS NOT NULL
                  OR NULLIF(BTRIM(COALESCE(tr.content, '')), '') IS NOT NULL
              )
            ORDER BY tr.created_at DESC NULLS LAST, tr.id DESC
            LIMIT 1
        ) t ON TRUE
        LEFT JOIN sources s ON rn.source_id = s.id
        {where_sql}
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
                ELSE t.title
            END AS title,
            CASE 
                WHEN rn.language_id = 1 THEN rn.content_original
                ELSE t.content
            END AS content,
            rn.url,
            s.name as source_name,
            'ar' as language_code,
            rn.published_at,
            rn.fetched_at
        FROM raw_news rn
        LEFT JOIN LATERAL (
            SELECT tr.id, tr.title, tr.content
            FROM translations tr
            WHERE tr.raw_news_id = rn.id
              AND tr.language_id = 1
              AND (
                  NULLIF(BTRIM(COALESCE(tr.title, '')), '') IS NOT NULL
                  OR NULLIF(BTRIM(COALESCE(tr.content, '')), '') IS NOT NULL
              )
            ORDER BY tr.created_at DESC NULLS LAST, tr.id DESC
            LIMIT 1
        ) t ON TRUE
        LEFT JOIN sources s ON rn.source_id = s.id
        WHERE rn.id = $1
        AND (rn.language_id = 1 OR t.id IS NOT NULL)
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
