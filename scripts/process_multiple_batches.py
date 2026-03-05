"""
Process multiple batches quickly
"""
import asyncio
import asyncpg
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.geo.location_processor import process_locations
from app.services.extraction.metrics_processor import process_metrics
from app.core.config import settings


async def main():
    pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=2,
        max_size=10,
        command_timeout=60
    )
    
    print("🚀 Processing multiple batches...\n")
    
    # Process locations (5 batches)
    print("📍 Processing Locations:")
    for i in range(5):
        result = await process_locations(pool, batch_size=10)
        if result['processed_news'] == 0:
            print(f"   Batch {i+1}: No more news")
            break
        print(f"   Batch {i+1}: {result['processed_news']} news → {result['events_created']} events")
    
    # Process metrics (10 batches)
    print("\n📊 Processing Metrics:")
    for i in range(10):
        result = await process_metrics(pool, batch_size=30)
        if result['processed_events'] == 0:
            print(f"   Batch {i+1}: No more events")
            break
        print(f"   Batch {i+1}: {result['processed_events']} events → {result['metrics_created']} metrics")
    
    await pool.close()
    print("\n✅ Done!")


if __name__ == "__main__":
    asyncio.run(main())
