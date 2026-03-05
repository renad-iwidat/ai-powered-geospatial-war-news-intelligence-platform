"""
Process all unprocessed news data
Runs location processor and metrics processor
"""
import asyncio
import asyncpg
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.geo.location_processor import process_locations
from app.services.extraction.metrics_processor import process_metrics
from app.core.config import settings


async def main():
    """Process all data"""
    
    print("=" * 80)
    print("🚀 GeoNews AI - Data Processing")
    print("=" * 80)
    
    # Connect to database
    pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=2,
        max_size=10,
        command_timeout=60
    )
    
    # Step 1: Process locations
    print("\n📍 Step 1: Processing Locations...")
    print("-" * 80)
    
    total_processed = 0
    total_places = 0
    total_locations = 0
    total_events = 0
    
    batch_num = 1
    while True:
        print(f"\n🔄 Batch {batch_num}...")
        result = await process_locations(pool, batch_size=20)
        
        if result['processed_news'] == 0:
            print("✅ No more news to process")
            break
        
        total_processed += result['processed_news']
        total_places += result['places_detected']
        total_locations += result['locations_upserted']
        total_events += result['events_created']
        
        print(f"   Processed: {result['processed_news']} news")
        print(f"   Detected: {result['places_detected']} places")
        print(f"   Created: {result['events_created']} events")
        
        batch_num += 1
        
        # Safety limit
        if batch_num > 15:
            print("\n⚠️  Reached batch limit (15 batches)")
            break
    
    print("\n" + "=" * 80)
    print("📊 Location Processing Summary:")
    print(f"   Total news processed: {total_processed}")
    print(f"   Total places detected: {total_places}")
    print(f"   Total locations stored: {total_locations}")
    print(f"   Total events created: {total_events}")
    print("=" * 80)
    
    # Step 2: Process metrics
    print("\n\n📊 Step 2: Processing Metrics...")
    print("-" * 80)
    
    total_events_processed = 0
    total_metrics_created = 0
    
    batch_num = 1
    while True:
        print(f"\n🔄 Batch {batch_num}...")
        result = await process_metrics(pool, batch_size=50)
        
        if result['processed_events'] == 0:
            print("✅ No more events to process")
            break
        
        total_events_processed += result['processed_events']
        total_metrics_created += result['metrics_created']
        
        print(f"   Processed: {result['processed_events']} events")
        print(f"   Created: {result['metrics_created']} metrics")
        
        batch_num += 1
        
        # Safety limit
        if batch_num > 10:
            print("\n⚠️  Reached batch limit (10 batches)")
            break
    
    print("\n" + "=" * 80)
    print("📊 Metrics Processing Summary:")
    print(f"   Total events processed: {total_events_processed}")
    print(f"   Total metrics created: {total_metrics_created}")
    print("=" * 80)
    
    await pool.close()
    
    print("\n✅ All processing complete!")


if __name__ == "__main__":
    asyncio.run(main())
