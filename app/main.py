"""
=============================================================================
GeoNews AI Backend - Main Application
=============================================================================
تطبيق FastAPI الرئيسي للـ GeoNews AI platform.

يوفر endpoints لـ:
- الحصول على الأخبار (snapshot, list, detail)
- معالجة الأماكن والـ metrics
- فحص صحة التطبيق

البنية:
- Startup/Shutdown: إدارة اتصالات قاعدة البيانات
- Health Check: فحص حالة التطبيق والـ DB
- News Endpoints: قراءة الأخبار بطرق مختلفة
- Processing Endpoints: تشغيل معالجات الأماكن والـ metrics
====================================================================

@app.get("/health")
async def health():
    pool = get_pool()
    try:
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return {"status": "ok", "db": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"db not ready: {str(e)}")
# ================================
# Startup Event
# ================================

@app.on_event("startup")
async def startup_event():
    """
    يتم تنفيذ هذه الدالة عند تشغيل السيرفر.

    الهدف:
    إنشاء connection pool لقاعدة البيانات.
    """

    try:
        await init_db()
    except Exception as e:
        print(f"Warning: Failed to initialize database: {e}")
        print("Server will continue running without database connection")


# ================================
# Shutdown Event
# ================================

@app.on_event("shutdown")
async def shutdown_event():
    """
    يتم تنفيذ هذه الدالة عند إيقاف السيرفر.

    الهدف:
    إغلاق جميع اتصالات قاعدة البيانات.
    """

    await close_db()


# ================================
# Snapshot Endpoint
# ================================




@app.get("/news/snapshot")
async def news_snapshot(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    limit = min(limit, MAX_SNAPSHOT_LIMIT)

    # 1) احصل على pool
    try:
        pool = get_pool()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database pool not initialized")

    # 2) عرّفي query (برا أي except)
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

    # ملاحظة: لا تحطي place_name/lat/lng/event_type إلا بعد ما تعملوا processor وview فيها هالأعمدة

    # 3) نفذي
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
from fastapi import Query, HTTPException
import asyncpg

@app.get("/news/list")
async def news_list(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: str | None = Query(None),
    place: str | None = Query(None),
    source: str = Query("auto", pattern="^(auto|raw|translation)$"),
):
    try:
        pool = get_pool()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database pool not initialized")

    # نبني WHERE + params
    where = []
    params = []
    i = 1

    # فلترة source_mode
    if source != "auto":
        where.append(f"source_mode = ${i}")
        params.append(source)
        i += 1

    # بحث في العنوان/المحتوى العربي
    if q:
        where.append(f"(title_ar ILIKE ${i} OR content_ar ILIKE ${i})")
        params.append(f"%{q}%")
        i += 1

    # فلترة مكان: لازم يكون عنده event بنفس place_name
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

    # إجمالي العدد للفرونت
    count_sql = f"SELECT COUNT(*) FROM vw_news_ar_feed {where_sql};"

    # عناصر الليست: content_preview بدل full content (للأداء)
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
@app.get("/news/{raw_news_id}")
async def news_detail(raw_news_id: int):
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
@app.post("/process/locations")
async def run_locations_processor(batch_size: int = Body(20)):
    try:
        pool = get_pool()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database pool not initialized")

    from .services.location_processor import process_locations
    return await process_locations(pool, batch_size=batch_size, sleep_seconds=1.0)

from fastapi import Body, HTTPException

@app.post("/process/metrics")
async def run_metrics_processor(batch_size: int = Body(50)):
    try:
        pool = get_pool()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database pool not initialized")

    from .services.metrics_processor import process_metrics
    return await process_metrics(pool, batch_size=batch_size)