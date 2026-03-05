"""
API Dependencies
Common dependencies for FastAPI endpoints
"""

import asyncpg
from app.core.database import get_db_pool


async def get_database() -> asyncpg.Pool:
    """Get database connection pool"""
    return await get_db_pool()
