"""
Check all locations in database
"""

import asyncio
import asyncpg
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def check_locations():
    """Check all locations in the database"""
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        # Get all locations
        locations = await conn.fetch("""
            SELECT id, name, country_code, latitude, longitude
            FROM locations
            ORDER BY name
        """)
        
        print(f"\n📍 All locations ({len(locations)}):")
        for loc in locations:
            print(f"  {loc['id']:3d}. {loc['name']:30s} ({loc['country_code']}) - Lat: {loc['latitude']:.4f}, Lon: {loc['longitude']:.4f}")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(check_locations())
