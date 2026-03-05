from typing import Optional
import asyncpg
from .settings import DATABASE_URL

# متغير global يحتفظ بالـ connection pool
_pool: Optional[asyncpg.Pool] = None


async def init_db():
    """
    يتم استدعاء هذه الدالة عند تشغيل السيرفر.
    وظيفتها إنشاء connection pool لقاعدة البيانات.

    Pool = مجموعة اتصالات جاهزة يتم إعادة استخدامها
    بدل فتح اتصال جديد لكل request.
    """

    global _pool

    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=DATABASE_URL,   # رابط الاتصال بقاعدة البيانات
            min_size=2,         # أقل عدد اتصالات مفتوحة
            max_size=10,        # أقصى عدد اتصالات
            command_timeout=30  # timeout لأي query
        )


async def close_db():
    """
    يتم استدعاء هذه الدالة عند إيقاف السيرفر.

    الهدف:
    إغلاق جميع الاتصالات المفتوحة بشكل نظيف.
    """

    global _pool

    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    """
    ترجع connection pool الحالي.

    نستخدمها داخل repository files
    لتنفيذ queries على قاعدة البيانات.
    """

    if _pool is None:
        raise RuntimeError("Database pool not initialized")

    return _pool