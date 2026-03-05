"""
Process one batch of data
Quick script to process small batches
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
    
    print("🔄 Processing locations (batch of 10)...")
    result = await process_locations(pool, batch_size=10)
    print(f"✅ Processed: {result['processed_news']} news, {result['events_created']} events")
    
    print("\n🔄 Processing metrics (batch of 20)...")
    result = await process_metrics(pool, batch_size=20)
    print(f"✅ Processed: {result['processed_events']} events, {result['metrics_created']} metrics")
    
    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
