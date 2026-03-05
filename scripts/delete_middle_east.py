"""
Delete Middle East location (duplicate of Iraq)
"""

import asyncio
import asyncpg
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def delete_middle_east():
    """Delete Middle East location"""
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        # First, check if there are any news_events linked to this location
        events = await conn.fetch("""
            SELECT id, raw_news_id
            FROM news_events
            WHERE location_id = 18
        """)
        
        print(f"\n=== Checking Dependencies ===")
        print(f"News events linked to 'الشرق الاوسط': {len(events)}")
        
        if events:
            print(f"\nUpdating {len(events)} news events to point to 'العراق' (ID: 63)...")
            # Update news_events to point to the correct Iraq location
            result = await conn.execute("""
                UPDATE news_events
                SET location_id = 63
                WHERE location_id = 18
            """)
            print(f"✅ Updated news events: {result}")
        
        # Now delete the Middle East location
        result = await conn.execute("""
            DELETE FROM locations
            WHERE id = 18
            AND name = 'الشرق الاوسط'
        """)
        print(f"\n✅ Deleted 'الشرق الاوسط' location: {result}")
        
        # Verify Iraq locations
        locations = await conn.fetch("""
            SELECT id, name, country_code, latitude, longitude
            FROM locations
            WHERE country_code = 'IQ'
            ORDER BY name
        """)
        
        print(f"\n📍 Remaining Iraq locations ({len(locations)}):")
        for loc in locations:
            print(f"  ID: {loc['id']:3d} | {loc['name']}")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(delete_middle_east())
