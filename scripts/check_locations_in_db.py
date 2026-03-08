#!/usr/bin/env python3
"""
Check locations in database
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def check_locations():
    """Check locations in database"""
    
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env")
        return False
    
    try:
        conn = await asyncpg.connect(database_url)
        
        print("📊 Checking Locations in Database")
        print("=" * 70)
        
        # Count locations
        count = await conn.fetchval("SELECT COUNT(*) FROM locations")
        print(f"\n✅ Total locations: {count}")
        
        # Show recent locations
        print("\n📋 Recent locations:")
        rows = await conn.fetch(
            """
            SELECT id, name, country_code, latitude, longitude, osm_id, osm_type
            FROM locations
            ORDER BY id DESC
            LIMIT 10
            """
        )
        
        for row in rows:
            print(f"  ID={row['id']}: {row['name']} ({row['country_code']}) - OSM:{row['osm_type']}/{row['osm_id']}")
        
        # Check for duplicates
        print("\n🔍 Checking for duplicate OSM IDs:")
        duplicates = await conn.fetch(
            """
            SELECT osm_type, osm_id, COUNT(*) as count
            FROM locations
            GROUP BY osm_type, osm_id
            HAVING COUNT(*) > 1
            """
        )
        
        if duplicates:
            print(f"  ⚠️  Found {len(duplicates)} duplicate OSM IDs:")
            for dup in duplicates:
                print(f"     - {dup['osm_type']}/{dup['osm_id']}: {dup['count']} times")
        else:
            print("  ✅ No duplicates found")
        
        # Check news_events
        print("\n📋 Checking news_events:")
        events_count = await conn.fetchval("SELECT COUNT(*) FROM news_events")
        print(f"  Total events: {events_count}")
        
        events_with_locations = await conn.fetchval(
            "SELECT COUNT(*) FROM news_events WHERE location_id IS NOT NULL"
        )
        print(f"  Events with locations: {events_with_locations}")
        
        # Show sample events
        print("\n  Sample events:")
        sample_events = await conn.fetch(
            """
            SELECT ne.id, ne.place_name, l.name, l.country_code
            FROM news_events ne
            LEFT JOIN locations l ON ne.location_id = l.id
            LIMIT 5
            """
        )
        
        for event in sample_events:
            loc_name = event['name'] or "NULL"
            print(f"    Event {event['id']}: {event['place_name']} → {loc_name} ({event['country_code']})")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(check_locations())
