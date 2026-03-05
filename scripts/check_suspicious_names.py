"""
Check for suspicious location names
"""

import asyncio
import asyncpg
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def check_suspicious():
    """Check for suspicious location names"""
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        # Check for locations with prefixes like "ل" (for)
        locations = await conn.fetch("""
            SELECT id, name, country_code, latitude, longitude
            FROM locations
            WHERE name LIKE 'ل%'
            OR name LIKE 'و%'
            OR name LIKE '%:' 
            OR name LIKE '%.%'
            ORDER BY name
        """)
        
        print(f"\n=== Suspicious Location Names ({len(locations)}) ===\n")
        for loc in locations:
            print(f"ID: {loc['id']:3d} | Name: {loc['name']:30s} | Code: {loc['country_code']} | Lat: {loc['latitude']:.4f}, Lon: {loc['longitude']:.4f}")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(check_suspicious())
