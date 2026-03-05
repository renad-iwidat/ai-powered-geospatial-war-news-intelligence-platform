"""
Clean up location names
"""

import asyncio
import asyncpg
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def clean_names():
    """Clean up location names"""
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        updates = []
        
        # Remove trailing colons
        result1 = await conn.execute("""
            UPDATE locations
            SET name = RTRIM(name, ':')
            WHERE name LIKE '%:'
        """)
        updates.append(f"Removed trailing colons: {result1}")
        
        # Remove trailing commas
        result2 = await conn.execute("""
            UPDATE locations
            SET name = RTRIM(name, '،')
            WHERE name LIKE '%،'
        """)
        updates.append(f"Removed trailing commas: {result2}")
        
        # Fix "لايران" → "إيران" (but keep "لبنان" as is)
        result3 = await conn.execute("""
            UPDATE locations
            SET name = 'إيران'
            WHERE name = 'لايران'
            AND country_code = 'PK'
        """)
        updates.append(f"Fixed 'لايران' to 'إيران': {result3}")
        
        # Fix "لاسرائيل" → "إسرائيل"
        result4 = await conn.execute("""
            UPDATE locations
            SET name = 'إسرائيل',
                country_code = 'IL'
            WHERE name = 'لاسرائيل'
        """)
        updates.append(f"Fixed 'لاسرائيل' to 'إسرائيل': {result4}")
        
        print("\n=== Cleanup Results ===\n")
        for update in updates:
            print(f"✅ {update}")
        
        # Show cleaned locations
        locations = await conn.fetch("""
            SELECT id, name, country_code
            FROM locations
            WHERE id IN (1, 2, 38, 110, 153, 332, 434, 443)
            ORDER BY id
        """)
        
        print(f"\n📍 Cleaned locations:")
        for loc in locations:
            print(f"  ID: {loc['id']:3d} | {loc['name']:30s} | {loc['country_code']}")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(clean_names())
