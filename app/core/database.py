"""
Database Connection Management
Handles PostgreSQL connection pool using asyncpg
"""

from typing import Optional
import asyncpg
from .config import settings


class DatabaseManager:
    """Manages database connection pool lifecycle"""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """Initialize database connection pool"""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                command_timeout=settings.DB_COMMAND_TIMEOUT
            )
    
    async def disconnect(self) -> None:
        """Close all database connections"""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
    
    def get_pool(self) -> asyncpg.Pool:
        """Get the current connection pool"""
        if self._pool is None:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
        return self._pool


# Global database manager instance
db_manager = DatabaseManager()


# Dependency for FastAPI endpoints
async def get_db_pool() -> asyncpg.Pool:
    """FastAPI dependency to get database pool"""
    return db_manager.get_pool()
