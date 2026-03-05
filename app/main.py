from fastapi import FastAPI, Query
from dotenv import load_dotenv

from .db import init_db, close_db, get_pool
from .settings import NEWS_VIEW_NAME, MAX_SNAPSHOT_LIMIT
import asyncpg
from fastapi import HTTPException, Query
# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="GeoNews API",
    description="Backend API for GeoNews AI platform",
    version="1.0"
)

from fastapi import HTTPException

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