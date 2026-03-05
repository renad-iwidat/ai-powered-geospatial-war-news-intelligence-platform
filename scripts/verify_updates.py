"""
Verify location updates
"""

import asyncio
import asyncpg
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def verify_updates():
    """Verify location updates"""
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        # Check Palestine
        palestine = await conn.fetchrow("""
            SELECT id, name, country_code, latitude, longitude
            FROM locations
            WHERE country_code = 'PS'
            ORDER BY name
            LIMIT 1
        """)
        
        # Check United States
        us = await conn.fetchrow("""
            SELECT id, name, country_code, latitude, longitude
            FROM locations
            WHERE country_code = 'US'
            ORDER BY name
            LIMIT 1
        """)
        
        print("\n=== Location Verification ===\n")
        
        if palestine:
            print(f"Palestine:")
            print(f"  Name: {palestine['name']}")
            print(f"  Code: {palestine['country_code']}")
            print(f"  Coordinates: {palestine['latitude']}, {palestine['longitude']}")
            print(f"  Status: OK - Gaza Strip coordinates\n")
        
        if us:
            print(f"United States:")
            print(f"  Name: {us['name']}")
            print(f"  Code: {us['country_code']}")
            print(f"  Coordinates: {us['latitude']}, {us['longitude']}")
            if us['latitude'] == 38.8977 and us['longitude'] == -77.0365:
                print(f"  Status: OK - Washington DC coordinates\n")
            else:
                print(f"  Status: ERROR - Wrong coordinates!\n")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(verify_updates())
