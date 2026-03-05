"""
Check all Palestine locations
"""

import asyncio
import asyncpg
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def check_palestine():
    """Check all Palestine locations"""
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        # Get all Palestine locations
        locations = await conn.fetch("""
            SELECT id, name, country_code, latitude, longitude
            FROM locations
            WHERE country_code = 'PS'
            ORDER BY name
        """)
        
        print(f"\n=== Palestine Locations ({len(locations)}) ===\n")
        for loc in locations:
            print(f"ID: {loc['id']:3d} | Name: {loc['name']:30s} | Lat: {loc['latitude']:.4f}, Lon: {loc['longitude']:.4f}")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(check_palestine())
