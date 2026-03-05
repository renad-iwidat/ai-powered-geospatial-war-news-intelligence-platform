"""
Update location names in database
- Replace "Gaza" with "Palestine"
- Replace "White House" with "United States"
"""

import asyncio
import asyncpg
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def update_location_names():
    """Update location names in the database"""
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        # Update Gaza to Palestine (غزه → فلسطين)
        result1 = await conn.execute("""
            UPDATE locations
            SET name = 'فلسطين'
            WHERE name = 'غزه'
            AND country_code = 'PS'
        """)
        print(f"✅ Updated Gaza to Palestine: {result1}")
        
        # Update White House to United States with correct coordinates (البيت الابيض → الولايات المتحدة)
        # Washington DC coordinates: 38.8977° N, 77.0365° W
        result2 = await conn.execute("""
            UPDATE locations
            SET name = 'الولايات المتحدة',
                country_code = 'US',
                latitude = 38.8977,
                longitude = -77.0365
            WHERE name = 'البيت الابيض'
        """)
        print(f"✅ Updated White House to United States with correct coordinates: {result2}")
        
        # Show updated locations
        locations = await conn.fetch("""
            SELECT id, name, country_code, latitude, longitude
            FROM locations
            WHERE name IN ('فلسطين', 'الولايات المتحدة')
            ORDER BY name
        """)
        
        print(f"\n📍 Updated locations ({len(locations)}):")
        for loc in locations:
            print(f"  - {loc['name']} ({loc['country_code']}) - Lat: {loc['latitude']}, Lon: {loc['longitude']}")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(update_location_names())
