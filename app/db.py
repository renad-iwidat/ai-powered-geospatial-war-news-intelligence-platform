"""
=============================================================================
Database Connection Management
=============================================================================
يدير اتصالات قاعدة البيانات PostgreSQL باستخدام asyncpg.
يستخدم Connection Pool لإعادة استخدام الاتصالات بكفاءة.
=============================================================================
"""

from typing import Optional
import asyncpg
from .settings import DATABASE_URL

# ============================================================================
# Global Connection Pool
# ============================================================================
# متغير global يحتفظ بـ connection pool واحد للتطبيق كله
_pool: Optional[asyncpg.Pool] = None


# ============================================================================
# Initialization
# ============================================================================
async def init_db():
    """
    إنشاء connection pool عند تشغيل السيرفر.
    
    يتم استدعاء هذه الدالة من startup_event في main.py
    
    Pool = مجموعة اتصالات جاهزة يتم إعادة استخدامها بدل فتح اتصال جديد لكل request.
    """
    global _pool

    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=DATABASE_URL,           # رابط الاتصال بقاعدة البيانات
            min_size=2,                 # أقل عدد اتصالات مفتوحة دائماً
            max_size=10,                # أقصى عدد اتصالات متزامنة
            command_timeout=30          # timeout لأي query (بالثواني)
        )


# ============================================================================
# Cleanup
# ============================================================================
async def close_db():
    """
    إغلاق جميع الاتصالات بشكل نظيف عند إيقاف السيرفر.
    
    يتم استدعاء هذه الدالة من shutdown_event في main.py
    """
    global _pool

    if _pool is not None:
        await _pool.close()
        _pool = None


# ============================================================================
# Get Pool
# ============================================================================
def get_pool() -> asyncpg.Pool:
    """
    الحصول على connection pool الحالي.
    
    يستخدم في جميع الـ services والـ endpoints للتواصل مع قاعدة البيانات.
    
    Raises:
        RuntimeError: إذا لم يتم تهيئة pool بعد (لم يتم استدعاء init_db)
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db() first.")

    return _pool