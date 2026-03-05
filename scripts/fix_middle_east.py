"""
Fix Middle East location to Iraq
"""

import asyncio
import asyncpg
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def fix_middle_east():
    """Fix Middle East location to Iraq"""
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        # Update Middle East to Iraq
        result = await conn.execute("""
            UPDATE locations
            SET name = 'العراق'
            WHERE name = 'الشرق الاوسط'
            AND country_code = 'IQ'
        """)
        print(f"✅ Updated Middle East to Iraq: {result}")
        
        # Show updated location
        location = await conn.fetchrow("""
            SELECT id, name, country_code, latitude, longitude
            FROM locations
            WHERE id = 18
        """)
        
        if location:
            print(f"\n📍 Updated location:")
            print(f"  ID: {location['id']}")
            print(f"  Name: {location['name']}")
            print(f"  Country Code: {location['country_code']}")
            print(f"  Coordinates: {location['latitude']}, {location['longitude']}")
            print(f"  Status: OK - Iraq (Baghdad area)")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(fix_middle_east())
