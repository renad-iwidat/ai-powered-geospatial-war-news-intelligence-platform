"""
Fix United States coordinates to Washington DC
"""

import asyncio
import asyncpg
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def fix_coordinates():
    """Fix United States coordinates"""
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        # Update coordinates for United States (Washington DC)
        result = await conn.execute("""
            UPDATE locations
            SET latitude = 38.8977,
                longitude = -77.0365
            WHERE name = 'الولايات المتحدة'
            AND country_code = 'US'
        """)
        print(f"✅ Updated United States coordinates: {result}")
        
        # Show updated location
        location = await conn.fetchrow("""
            SELECT id, name, country_code, latitude, longitude
            FROM locations
            WHERE name = 'الولايات المتحدة'
            AND country_code = 'US'
        """)
        
        if location:
            print(f"\n📍 Updated location:")
            print(f"  - {location['name']} ({location['country_code']}) - Lat: {location['latitude']}, Lon: {location['longitude']}")
            print(f"  - This is Washington DC, United States")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(fix_coordinates())
