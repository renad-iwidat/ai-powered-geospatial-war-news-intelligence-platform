#!/usr/bin/env python3
"""
Final summary of data processing
"""

import asyncio
import httpx
import asyncpg
import os
from dotenv import load_dotenv
from datetime import date

async def get_summary():
    """Get final summary"""
    
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    api_base_url = "http://localhost:8000"
    
    print("📊 FINAL DATA PROCESSING SUMMARY")
    print("=" * 70)
    
    # Get API status
    print("\n🔗 API Status:")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{api_base_url}/api/v1/data-processing/status")
            response.raise_for_status()
            status = response.json()
            
            print(f"  ✅ Total Articles: {status['total_articles']}")
            print(f"  ✅ Articles with Events: {status['articles_with_events']}")
            print(f"  ✅ Articles without Events: {status['articles_without_events']}")
            print(f"  ✅ Total Events: {status['total_events']}")
            print(f"  ✅ Events with Metrics: {status['events_with_metrics']}")
            print(f"  ✅ Events without Metrics: {status['events_without_metrics']}")
            print(f"  ✅ Overall Completion: {status['processing_completion_percentage']}%")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
    
    # Get today's analytics
    print("\n📅 Today's Analytics (7 March 2026):")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{api_base_url}/api/v1/analytics/by-date?days=14")
            response.raise_for_status()
            data = response.json()
            
            today_stats = None
            for day_stat in data['daily_stats']:
                if day_stat['date'] == str(date.today()):
                    today_stats = day_stat
                    break
            
            if today_stats:
                print(f"  ✅ Articles: {today_stats['articles_count']}")
                print(f"  ✅ Events: {today_stats['events_count']}")
                print(f"  ✅ Metrics: {today_stats['metrics_count']}")
            else:
                print("  ⚠️  No data for today yet")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
    
    # Get database stats
    print("\n💾 Database Statistics:")
    try:
        conn = await asyncpg.connect(database_url)
        
        locations_count = await conn.fetchval("SELECT COUNT(*) FROM locations")
        events_count = await conn.fetchval("SELECT COUNT(*) FROM news_events")
        metrics_count = await conn.fetchval("SELECT COUNT(*) FROM event_metrics")
        
        print(f"  ✅ Locations: {locations_count}")
        print(f"  ✅ Events: {events_count}")
        print(f"  ✅ Metrics: {metrics_count}")
        
        # Get top countries
        print("\n  🌍 Top Countries by Events:")
        top_countries = await conn.fetch(
            """
            SELECT l.country_code, COUNT(*) as count
            FROM news_events ne
            JOIN locations l ON ne.location_id = l.id
            GROUP BY l.country_code
            ORDER BY count DESC
            LIMIT 5
            """
        )
        
        for country in top_countries:
            print(f"     - {country['country_code']}: {country['count']} events")
        
        # Get top metrics
        print("\n  📊 Top Metrics:")
        top_metrics = await conn.fetch(
            """
            SELECT metric_type, COUNT(*) as count
            FROM event_metrics
            GROUP BY metric_type
            ORDER BY count DESC
            LIMIT 5
            """
        )
        
        for metric in top_metrics:
            print(f"     - {metric['metric_type']}: {metric['count']}")
        
        await conn.close()
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
    
    print("\n" + "=" * 70)
    print("✅ Summary Complete!")

if __name__ == "__main__":
    asyncio.run(get_summary())
