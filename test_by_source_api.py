#!/usr/bin/env python3
"""
Test script for the new by-source API endpoint
"""

import asyncio
import asyncpg
from app.core.config import settings

async def test_by_source_endpoint():
    """Test the by-source endpoint"""
    
    # Connect to database
    pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL)
    
    try:
        async with pool.acquire() as conn:
            # Test 1: Get articles from source 17 (Annahar)
            print("Test 1: Getting articles from source 17 (Annahar)")
            query = """
                SELECT DISTINCT
                    rn.id,
                    rn.title_original as title,
                    rn.content_original as content,
                    rn.url,
                    s.name as source_name,
                    s.id as source_id,
                    'ar' as language_code,
                    rn.published_at,
                    rn.fetched_at
                FROM raw_news rn
                LEFT JOIN sources s ON rn.source_id = s.id
                WHERE rn.source_id = $1
                ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC NULLS LAST
                LIMIT 5
            """
            rows = await conn.fetch(query, 17)
            print(f"Found {len(rows)} articles from source 17")
            for row in rows:
                print(f"  - {row['title'][:50]}... (ID: {row['id']})")
            
            # Test 2: Get total count from source 17
            print("\nTest 2: Getting total count from source 17")
            count_query = """
                SELECT COUNT(DISTINCT rn.id)
                FROM raw_news rn
                WHERE rn.source_id = $1
            """
            total = await conn.fetchval(count_query, 17)
            print(f"Total articles from source 17: {total}")
            
            # Test 3: Get source name
            print("\nTest 3: Getting source name")
            source_query = "SELECT name FROM sources WHERE id = $1"
            source_row = await conn.fetchrow(source_query, 17)
            if source_row:
                print(f"Source name: {source_row['name']}")
            
            # Test 4: Test with search
            print("\nTest 4: Testing search functionality")
            search_query = """
                SELECT DISTINCT
                    rn.id,
                    rn.title_original as title
                FROM raw_news rn
                WHERE rn.source_id = $1 AND rn.title_original ILIKE $2
                LIMIT 5
            """
            search_rows = await conn.fetch(search_query, 17, "%الحرب%")
            print(f"Found {len(search_rows)} articles matching 'الحرب'")
            
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(test_by_source_endpoint())
