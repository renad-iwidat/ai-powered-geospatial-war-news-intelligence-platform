"""
GeoNews API Backend
Main application entry point with all endpoints
"""

from fastapi import FastAPI, Query, HTTPException, Body
from dotenv import load_dotenv
import asyncpg

from .db import init_db, close_db, get_pool
from .settings import NEWS_VIEW_NAME, MAX_SNAPSHOT_LIMIT
from .services.metrics_processor import process_metrics
from .services.location_processor import process_locations

load_dotenv()

# ============================================================================
# Application Setup
# ============================================================================

app = FastAPI(
    title="GeoNews API",
    description="Backend API for GeoNews AI platform",
    version="1.0"
)


# ============================================================================
# Lifecycle Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool on server startup"""
    try:
        await init_db()
    except Exception as e:
        print(f"Warning: Failed to initialize database: {e}")
        print("Server will continue running without database connection")


@app.on_event("shutdown")
async def shutdown_event():
    """Close all database connections on server shutdown"""
    await close_db()


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/health")
async def health():
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return {"status": "ok", "db": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"db not ready: {str(e)}")

# ============================================================================
# News Endpoints
# ============================================================================

@app.get("/news/snapshot")
async def news_snapshot(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """
    Get a snapshot of recent news articles
    
    Returns latest news ordered by publication date with pagination
    """
    limit = min(limit, MAX_SNAPSHOT_LIMIT)

    try:
        pool = get_pool()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database pool not initialized")

    query = f"""
    SELECT
      raw_news_id AS id,
      url,
      published_at,
      fetched_at,
      title_ar AS title,
      content_ar AS content,
      source_name,
      has_numbers
    FROM {NEWS_VIEW_NAME}
    ORDER BY COALESCE(published_at, fetched_at) DESC NULLS LAST
    LIMIT $1 OFFSET $2
    """

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, limit, offset)
    except asyncpg.UndefinedTableError:
        raise HTTPException(status_code=500, detail=f"View not found: {NEWS_VIEW_NAME}")
    except asyncpg.UndefinedColumnError as e:
        raise HTTPException(status_code=500, detail=f"Missing column in view: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    return {"count": len(rows), "items": [dict(r) for r in rows]}


@app.get("/news/list")
async def news_list(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: str | None = Query(None),
    place: str | None = Query(None),
    source: str = Query("auto", pattern="^(auto|raw|translation)$"),
):
    """
    Get filtered list of news articles with search and location filtering
    
    Parameters:
    - q: Search query for title or content
    - place: Filter by location/place name
    - source: Filter by source mode (auto, raw, translation)
    """
    try:
        pool = get_pool()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database pool not initialized")

    # Build WHERE clause dynamically
    where = []
    params = []
    i = 1

    if source != "auto":
        where.append(f"source_mode = ${i}")
        params.append(source)
        i += 1

    if q:
        where.append(f"(title_ar ILIKE ${i} OR content_ar ILIKE ${i})")
        params.append(f"%{q}%")
        i += 1

    if place:
        where.append(f"""
        EXISTS (
          SELECT 1 FROM news_events ne
          WHERE ne.raw_news_id = raw_news_id
            AND ne.place_name = ${i}
        )
        """)
        params.append(place)
        i += 1

    where_sql = "WHERE " + " AND ".join(where) if where else ""

    # Get total count
    count_sql = f"SELECT COUNT(*) FROM vw_news_ar_feed {where_sql};"

    # Get paginated list with preview
    list_sql = f"""
      SELECT
        raw_news_id,
        url,
        COALESCE(published_at, fetched_at) AS sort_time,
        title_ar AS title,
        LEFT(content_ar, 220) AS content_preview,
        TRUE AS content_full_available,
        'ar' AS language_code,
        source_mode,
        has_numbers,
        events_count,
        metrics_count
      FROM vw_news_ar_feed
      {where_sql}
      ORDER BY COALESCE(published_at, fetched_at) DESC NULLS LAST
      LIMIT ${i} OFFSET ${i+1};
    """
    params.extend([limit, offset])

    try:
        async with pool.acquire() as conn:
            total = await conn.fetchval(count_sql, *params[:-2]) if where else await conn.fetchval("SELECT COUNT(*) FROM vw_news_ar_feed;")
            rows = await conn.fetch(list_sql, *params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    return {
        "items": [dict(r) for r in rows],
        "limit": limit,
        "offset": offset,
        "total": int(total),
    }


@app.get("/news/{raw_news_id}")
async def news_detail(raw_news_id: int):
    """
    Get detailed information about a specific news article
    
    Includes: full content, locations mentioned, and extracted metrics
    """
    try:
        pool = get_pool()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database pool not initialized")

    news_sql = """
      SELECT
        raw_news_id,
        title_ar AS title,
        content_ar AS content,
        url,
        source_mode,
        COALESCE(published_at, fetched_at) AS published_at
      FROM vw_news_ar_feed
      WHERE raw_news_id = $1
      LIMIT 1;
    """

    places_sql = """
      SELECT DISTINCT place_name
      FROM news_events
      WHERE raw_news_id = $1
      ORDER BY place_name;
    """

    metrics_sql = """
      SELECT em.metric_type, em.value
      FROM news_events ne
      JOIN event_metrics em ON em.event_id = ne.id
      WHERE ne.raw_news_id = $1
      ORDER BY em.metric_type, em.value DESC;
    """

    async with pool.acquire() as conn:
        item = await conn.fetchrow(news_sql, raw_news_id)
        if not item:
            raise HTTPException(status_code=404, detail="News not found")

        places = await conn.fetch(places_sql, raw_news_id)
        metrics = await conn.fetch(metrics_sql, raw_news_id)

    return {
        **dict(item),
        "places": [p["place_name"] for p in places],
        "metrics": [dict(m) for m in metrics],
    }


# ============================================================================
# Location Endpoints
# ============================================================================

@app.get("/places")
async def places_list(limit: int = Query(200, ge=1, le=2000)):
    """
    Get list of all locations mentioned in news articles
    
    Returns locations sorted by frequency of mention
    """
    try:
        pool = get_pool()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database pool not initialized")

    sql = """
      SELECT place_name, COUNT(*) AS c
      FROM news_events
      GROUP BY place_name
      ORDER BY c DESC, place_name ASC
      LIMIT $1;
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, limit)

    return {"items": [r["place_name"] for r in rows]}


# ============================================================================
# Processing Endpoints
# ============================================================================

@app.post("/process/locations")
async def run_locations_processor(batch_size: int = Body(20)):
    """
    Trigger location processing for news articles
    
    Extracts and geocodes locations from news content
    """
    try:
        pool = get_pool()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database pool not initialized")

    return await process_locations(pool, batch_size=batch_size, sleep_seconds=1.0)


@app.post("/process/metrics")
async def run_metrics_processor(batch_size: int = Body(50)):
    """
    Trigger metrics extraction for news articles
    
    Extracts numerical metrics (casualties, weapons, etc.) from news content
    """
    try:
        pool = get_pool()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database pool not initialized")

    return await process_metrics(pool, batch_size=batch_size)
