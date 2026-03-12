"""
Sources Endpoints
API endpoints for managing news sources
"""

from fastapi import APIRouter, Query, HTTPException, Depends
import asyncpg

from app.core.database import get_db_pool
from app.schemas import (
    SourceListResponse,
    SourceListItem,
    SourceDetail,
    SourceStatusResponse
)

router = APIRouter()


@router.get("", response_model=SourceListResponse)
async def get_sources_list(
    active_only: bool = Query(False, description="Filter only active sources"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get list of all news sources with their status
    
    - **active_only**: Filter to show only active sources
    """
    
    # Build WHERE clause
    where_clause = ""
    if active_only:
        where_clause = "WHERE s.is_active = true"
    
    # Get all sources with their details
    query = f"""
        SELECT
            s.id,
            s.name,
            s.url,
            s.is_active,
            s.source_type_id,
            st.name as source_type_name,
            COUNT(rn.id) as articles_count
        FROM sources s
        LEFT JOIN source_types st ON s.source_type_id = st.id
        LEFT JOIN raw_news rn ON s.id = rn.source_id
        {where_clause}
        GROUP BY s.id, s.name, s.url, s.is_active, s.source_type_id, st.name
        ORDER BY s.is_active DESC, s.name ASC
    """
    
    # Get total counts
    count_query = """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN is_active = true THEN 1 END) as active_count,
            COUNT(CASE WHEN is_active = false THEN 1 END) as inactive_count
        FROM sources
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        count_row = await conn.fetchrow(count_query)
    
    items = [SourceListItem(**dict(row)) for row in rows]
    
    return SourceListResponse(
        items=items,
        total=count_row['total'],
        active_count=count_row['active_count'],
        inactive_count=count_row['inactive_count']
    )


@router.get("/status/active", response_model=SourceListResponse)
async def get_active_sources(
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get list of all active sources
    """
    
    query = """
        SELECT
            s.id,
            s.name,
            s.url,
            s.is_active,
            s.source_type_id,
            st.name as source_type_name,
            COUNT(rn.id) as articles_count
        FROM sources s
        LEFT JOIN source_types st ON s.source_type_id = st.id
        LEFT JOIN raw_news rn ON s.id = rn.source_id
        WHERE s.is_active = true
        GROUP BY s.id, s.name, s.url, s.is_active, s.source_type_id, st.name
        ORDER BY s.name ASC
    """
    
    count_query = """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN is_active = true THEN 1 END) as active_count,
            COUNT(CASE WHEN is_active = false THEN 1 END) as inactive_count
        FROM sources
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        count_row = await conn.fetchrow(count_query)
    
    items = [SourceListItem(**dict(row)) for row in rows]
    
    return SourceListResponse(
        items=items,
        total=count_row['total'],
        active_count=count_row['active_count'],
        inactive_count=count_row['inactive_count']
    )


@router.get("/status/inactive", response_model=SourceListResponse)
async def get_inactive_sources(
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get list of all inactive sources
    """
    
    query = """
        SELECT
            s.id,
            s.name,
            s.url,
            s.is_active,
            s.source_type_id,
            st.name as source_type_name,
            COUNT(rn.id) as articles_count
        FROM sources s
        LEFT JOIN source_types st ON s.source_type_id = st.id
        LEFT JOIN raw_news rn ON s.id = rn.source_id
        WHERE s.is_active = false
        GROUP BY s.id, s.name, s.url, s.is_active, s.source_type_id, st.name
        ORDER BY s.name ASC
    """
    
    count_query = """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN is_active = true THEN 1 END) as active_count,
            COUNT(CASE WHEN is_active = false THEN 1 END) as inactive_count
        FROM sources
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        count_row = await conn.fetchrow(count_query)
    
    items = [SourceListItem(**dict(row)) for row in rows]
    
    return SourceListResponse(
        items=items,
        total=count_row['total'],
        active_count=count_row['active_count'],
        inactive_count=count_row['inactive_count']
    )


@router.get("/{source_id}", response_model=SourceDetail)
async def get_source_detail(
    source_id: int,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get detailed information about a specific source
    
    - **source_id**: The ID of the source
    """
    
    query = """
        SELECT
            s.id,
            s.name,
            s.url,
            s.is_active,
            s.source_type_id,
            st.name as source_type_name,
            s.created_at,
            COUNT(rn.id) as articles_count
        FROM sources s
        LEFT JOIN source_types st ON s.source_type_id = st.id
        LEFT JOIN raw_news rn ON s.id = rn.source_id
        WHERE s.id = $1
        GROUP BY s.id, s.name, s.url, s.is_active, s.source_type_id, st.name, s.created_at
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, source_id)
    
    if not row:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return SourceDetail(**dict(row))


@router.get("/{source_id}/status", response_model=SourceStatusResponse)
async def get_source_status(
    source_id: int,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Get the status of a specific source (Active/Inactive)
    
    - **source_id**: The ID of the source
    """
    
    query = """
        SELECT
            s.id,
            s.name,
            s.is_active,
            COUNT(rn.id) as articles_count
        FROM sources s
        LEFT JOIN raw_news rn ON s.id = rn.source_id
        WHERE s.id = $1
        GROUP BY s.id, s.name, s.is_active
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, source_id)
    
    if not row:
        raise HTTPException(status_code=404, detail="Source not found")
    
    status = "Active" if row['is_active'] else "Inactive"
    
    return SourceStatusResponse(
        id=row['id'],
        name=row['name'],
        is_active=row['is_active'],
        status=status,
        articles_count=row['articles_count']
    )
