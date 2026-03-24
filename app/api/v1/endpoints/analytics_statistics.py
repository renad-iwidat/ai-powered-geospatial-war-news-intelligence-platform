"""
Analytics & Statistics Endpoints
API endpoints for analytics and statistical data
"""

from fastapi import APIRouter, Query, Depends
from datetime import date, timedelta
import asyncpg

from app.core.database import get_db_pool
from app.schemas import (
    AnalyticsOverview,
    CountryStatisticsResponse,
    CountryStatistics,
    DateStatisticsResponse,
    DateStatistics,
    TimelineResponse,
    TimelineItem
)

router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get overview analytics with key statistics
    
    Returns comprehensive statistics about the entire dataset
    """
    
    async with pool.acquire() as conn:
        # Total counts
        total_news = await conn.fetchval("SELECT COUNT(*) FROM raw_news")
        total_locations = await conn.fetchval("SELECT COUNT(*) FROM locations")
        total_events = await conn.fetchval("SELECT COUNT(*) FROM news_events")
        total_metrics = await conn.fetchval("SELECT COUNT(*) FROM event_metrics")
        total_countries = await conn.fetchval("SELECT COUNT(DISTINCT country_code) FROM locations")
        
        # Articles with/without events
        articles_with_events = await conn.fetchval(
            "SELECT COUNT(DISTINCT raw_news_id) FROM news_events"
        )
        articles_without_events = total_news - articles_with_events
        
        # Events with/without metrics
        events_with_metrics = await conn.fetchval(
            "SELECT COUNT(DISTINCT event_id) FROM event_metrics"
        )
        events_without_metrics = total_events - events_with_metrics
    
    return AnalyticsOverview(
        total_news_articles=total_news,
        total_locations=total_locations,
        total_events=total_events,
        total_metrics=total_metrics,
        total_countries=total_countries,
        articles_with_events=articles_with_events,
        articles_without_events=articles_without_events,
        events_with_metrics=events_with_metrics,
        events_without_metrics=events_without_metrics
    )



@router.get("/by-country", response_model=CountryStatisticsResponse)
async def get_analytics_by_country(
    limit: int = Query(50, ge=1, le=200, description="Number of countries"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get statistics grouped by country
    
    - **limit**: Number of countries to return (1-200)
    
    Returns statistics for each country including locations, events, and metrics counts
    """
    
    query = """
        SELECT
            l.country_code,
            l.country_code as country_name,
            COUNT(DISTINCT l.id) as locations_count,
            COUNT(DISTINCT ne.id) as events_count,
            COUNT(DISTINCT em.id) as metrics_count
        FROM locations l
        LEFT JOIN news_events ne ON l.id = ne.location_id
        LEFT JOIN event_metrics em ON ne.id = em.event_id
        GROUP BY l.country_code
        ORDER BY events_count DESC, locations_count DESC
        LIMIT $1
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, limit)
        total_countries = await conn.fetchval("SELECT COUNT(DISTINCT country_code) FROM locations")
    
    countries = [CountryStatistics(**dict(row)) for row in rows]
    
    return CountryStatisticsResponse(
        countries=countries,
        total_countries=total_countries
    )


@router.get("/by-date", response_model=DateStatisticsResponse)
async def get_analytics_by_date(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get daily statistics for the specified number of days
    
    - **days**: Number of days to include (1-365)
    
    Returns daily counts of articles, events, and metrics
    """
    
    query = """
        SELECT
            DATE(COALESCE(rn.published_at, rn.fetched_at)) as date,
            COUNT(DISTINCT rn.id) as articles_count,
            COUNT(DISTINCT ne.id) as events_count,
            COUNT(DISTINCT em.id) as metrics_count
        FROM raw_news rn
        LEFT JOIN news_events ne ON rn.id = ne.raw_news_id
        LEFT JOIN event_metrics em ON ne.id = em.event_id
        WHERE COALESCE(rn.published_at, rn.fetched_at) >= CURRENT_DATE - ($1 || ' days')::interval
        GROUP BY DATE(COALESCE(rn.published_at, rn.fetched_at))
        ORDER BY date DESC
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, str(days))
    
    daily_stats = [DateStatistics(**dict(row)) for row in rows]
    
    date_range_end = date.today()
    date_range_start = date_range_end - timedelta(days=days)
    
    return DateStatisticsResponse(
        daily_stats=daily_stats,
        date_range_start=date_range_start,
        date_range_end=date_range_end
    )



@router.get("/timeline", response_model=TimelineResponse)
async def get_analytics_timeline(
    limit: int = Query(50, ge=1, le=200, description="Number of items"),
    country_code: str = Query(None, description="Filter by country code"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get timeline of events with metrics
    
    - **limit**: Number of timeline items (1-200)
    - **country_code**: Filter by country code (optional)
    
    Returns chronological list of events with associated metrics
    """
    
    # Build WHERE clause
    extra_filters = []
    params = []
    param_idx = 1
    
    if country_code:
        extra_filters.append("l.country_code = $1")
        params.append(country_code.upper())
        param_idx += 1
    
    params.append(limit)
    
    query = f"""
        SELECT
            DATE(COALESCE(rn.published_at, rn.fetched_at)) as date,
            ne.id as event_id,
            l.name as location_name,
            l.country_code,
            CASE
                WHEN rn.language_id = 1 THEN rn.title_original
                ELSE t.title
            END as news_title,
            json_object_agg(
                em.metric_type,
                em.value
            ) FILTER (WHERE em.metric_type IS NOT NULL) as metrics
        FROM news_events ne
        LEFT JOIN locations l ON ne.location_id = l.id
        LEFT JOIN raw_news rn ON ne.raw_news_id = rn.id
        LEFT JOIN LATERAL (
            SELECT tr.id, tr.title
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
        LEFT JOIN event_metrics em ON ne.id = em.event_id
        WHERE (rn.language_id = 1 OR t.id IS NOT NULL)
        {"AND " + " AND ".join(extra_filters) if extra_filters else ""}
        GROUP BY ne.id, l.name, l.country_code, CASE
            WHEN rn.language_id = 1 THEN rn.title_original
            ELSE t.title
        END, rn.published_at, rn.fetched_at
        ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC NULLS LAST
        LIMIT ${param_idx}
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
    
    timeline = []
    for row in rows:
        item_dict = dict(row)
        # Convert metrics from JSON to dict
        if item_dict['metrics'] is None:
            item_dict['metrics'] = {}
        timeline.append(TimelineItem(**item_dict))
    
    return TimelineResponse(
        timeline=timeline,
        total_items=len(timeline)
    )


@router.get("/metrics-breakdown")
async def get_metrics_breakdown(
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get breakdown of metrics by type with totals
    
    Returns statistics for each metric type including count and total value
    """
    
    query = """
        SELECT
            metric_type,
            COUNT(*) as occurrences,
            SUM(value) as total_value,
            AVG(value) as average_value,
            MAX(value) as max_value
        FROM event_metrics
        GROUP BY metric_type
        ORDER BY total_value DESC
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
    
    return {
        "metrics": [dict(row) for row in rows],
        "total_types": len(rows)
    }


@router.get("/top-sources")
async def get_top_sources(
    limit: int = Query(10, ge=1, le=50, description="Number of sources"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get top news sources by article count
    
    - **limit**: Number of sources to return (1-50)
    
    Returns list of sources with their article counts and percentages
    """
    
    query = """
        SELECT
            s.name as source_name,
            st.name as source_type,
            COUNT(rn.id) as articles_count,
            COUNT(DISTINCT ne.id) as events_count,
            ROUND(COUNT(rn.id) * 100.0 / (SELECT COUNT(*) FROM raw_news), 2) as percentage
        FROM sources s
        LEFT JOIN source_types st ON s.source_type_id = st.id
        LEFT JOIN raw_news rn ON s.id = rn.source_id
        LEFT JOIN news_events ne ON rn.id = ne.raw_news_id
        WHERE s.is_active = true
        GROUP BY s.id, s.name, st.name
        ORDER BY articles_count DESC
        LIMIT $1
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, limit)
        total_sources = await conn.fetchval("SELECT COUNT(*) FROM sources WHERE is_active = true")
    
    return {
        "sources": [dict(row) for row in rows],
        "total_sources": total_sources
    }


@router.get("/hot-locations")
async def get_hot_locations(
    limit: int = Query(15, ge=1, le=50, description="Number of locations"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get hottest locations by event count
    
    - **limit**: Number of locations to return (1-50)
    
    Returns list of locations with highest event activity
    """
    
    query = """
        SELECT
            l.id,
            l.name as location_name,
            l.country_code,
            l.latitude,
            l.longitude,
            COUNT(DISTINCT ne.id) as events_count,
            COUNT(DISTINCT em.id) as metrics_count,
            COUNT(DISTINCT ne.raw_news_id) as articles_count
        FROM locations l
        LEFT JOIN news_events ne ON l.id = ne.location_id
        LEFT JOIN event_metrics em ON ne.id = em.event_id
        GROUP BY l.id, l.name, l.country_code, l.latitude, l.longitude
        HAVING COUNT(DISTINCT ne.id) > 0
        ORDER BY events_count DESC, metrics_count DESC
        LIMIT $1
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, limit)
    
    return {
        "locations": [dict(row) for row in rows],
        "total_count": len(rows)
    }


@router.get("/media-types")
async def get_media_types_distribution(
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get distribution of news by media type (source type)
    
    Returns statistics for each media type including article counts and percentages
    """
    
    query = """
        SELECT
            st.name as media_type,
            st.description,
            COUNT(DISTINCT s.id) as sources_count,
            COUNT(DISTINCT rn.id) as articles_count,
            COUNT(DISTINCT ne.id) as events_count,
            ROUND(COUNT(DISTINCT rn.id) * 100.0 / (SELECT COUNT(*) FROM raw_news), 2) as percentage
        FROM source_types st
        LEFT JOIN sources s ON st.id = s.source_type_id
        LEFT JOIN raw_news rn ON s.id = rn.source_id
        LEFT JOIN news_events ne ON rn.id = ne.raw_news_id
        GROUP BY st.id, st.name, st.description
        ORDER BY articles_count DESC
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
    
    return {
        "media_types": [dict(row) for row in rows],
        "total_types": len(rows)
    }


@router.get("/language-distribution")
async def get_language_distribution(
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get distribution of news by original language
    
    Returns statistics for each language including article counts and percentages
    """
    
    query = """
        SELECT
            l.code as language_code,
            l.name as language_name,
            COUNT(DISTINCT rn.id) as articles_count,
            COUNT(DISTINCT ne.id) as events_count,
            COUNT(DISTINCT t.id) as translations_count,
            ROUND(COUNT(DISTINCT rn.id) * 100.0 / (SELECT COUNT(*) FROM raw_news), 2) as percentage
        FROM languages l
        LEFT JOIN raw_news rn ON l.id = rn.language_id
        LEFT JOIN news_events ne ON rn.id = ne.raw_news_id
        LEFT JOIN translations t ON rn.id = t.raw_news_id
        GROUP BY l.id, l.code, l.name
        HAVING COUNT(DISTINCT rn.id) > 0
        ORDER BY articles_count DESC
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
    
    return {
        "languages": [dict(row) for row in rows],
        "total_languages": len(rows)
    }


@router.get("/activity-heatmap")
async def get_activity_heatmap(
    days: int = Query(30, ge=7, le=90, description="Number of days"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get activity heatmap data (day of week and hour patterns)
    
    - **days**: Number of days to analyze (7-90)
    
    Returns activity patterns by day of week and hour
    """
    
    query = """
        SELECT
            EXTRACT(DOW FROM COALESCE(rn.published_at, rn.fetched_at)) as day_of_week,
            EXTRACT(HOUR FROM COALESCE(rn.published_at, rn.fetched_at)) as hour_of_day,
            COUNT(DISTINCT rn.id) as articles_count,
            COUNT(DISTINCT ne.id) as events_count
        FROM raw_news rn
        LEFT JOIN news_events ne ON rn.id = ne.raw_news_id
        WHERE COALESCE(rn.published_at, rn.fetched_at) >= CURRENT_DATE - ($1 || ' days')::interval
        GROUP BY day_of_week, hour_of_day
        ORDER BY day_of_week, hour_of_day
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, str(days))
    
    return {
        "heatmap_data": [dict(row) for row in rows],
        "days_analyzed": days
    }


@router.get("/top-metrics-by-country")
async def get_top_metrics_by_country(
    limit: int = Query(10, ge=1, le=50, description="Number of metrics to return"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get top metrics with country information
    
    - **limit**: Number of metrics to return (1-50)
    
    Returns top metrics grouped by type with country breakdown
    """
    
    query = """
        WITH metric_countries AS (
            SELECT
                em.metric_type,
                l.country_code,
                COUNT(*) as occurrences,
                SUM(em.value) as total_value,
                AVG(em.value)::float as avg_value,
                MAX(em.value) as max_value
            FROM event_metrics em
            JOIN news_events ne ON em.event_id = ne.id
            LEFT JOIN locations l ON ne.location_id = l.id
            GROUP BY em.metric_type, l.country_code
        ),
        metric_totals AS (
            SELECT
                metric_type,
                SUM(occurrences) as total_occurrences,
                SUM(total_value) as total_value,
                AVG(avg_value)::float as overall_avg,
                MAX(max_value) as overall_max
            FROM metric_countries
            GROUP BY metric_type
        )
        SELECT
            mt.metric_type,
            mt.total_occurrences,
            mt.overall_avg,
            mt.overall_max,
            json_agg(
                json_build_object(
                    'country_code', mc.country_code,
                    'occurrences', mc.occurrences,
                    'avg_value', mc.avg_value,
                    'max_value', mc.max_value
                ) ORDER BY mc.occurrences DESC
            ) as countries
        FROM metric_totals mt
        JOIN metric_countries mc ON mt.metric_type = mc.metric_type
        GROUP BY mt.metric_type, mt.total_occurrences, mt.overall_avg, mt.overall_max
        ORDER BY mt.total_occurrences DESC
        LIMIT $1
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, limit)
    
    return {
        "metrics": [dict(row) for row in rows],
        "total_types": len(rows)
    }
