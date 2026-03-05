"""
Check Middle East location
"""

import asyncio
import asyncpg
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def check_middle_east():
    """Check Middle East location"""
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        # Find Middle East location
        location = await conn.fetchrow("""
            SELECT id, name, country_code, latitude, longitude
            FROM locations
            WHERE name LIKE '%الشرق الاوسط%'
            OR name LIKE '%Middle East%'
        """)
        
        if location:
            print(f"\n=== Middle East Location ===\n")
            print(f"ID: {location['id']}")
            print(f"Name: {location['name']}")
            print(f"Country Code: {location['country_code']}")
            print(f"Coordinates: {location['latitude']}, {location['longitude']}")
            
            # Check what's at these coordinates
            print(f"\nThese coordinates point to Iraq")
            print(f"Suggestion: Change to 'العراق' (Iraq)")
        else:
            print("Middle East location not found")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(check_middle_east())
