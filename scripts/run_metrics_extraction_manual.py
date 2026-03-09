#!/usr/bin/env python3
"""
Manual Metrics Extraction
تشغيل استخراج المؤشرات يدويّاً
"""

import sys
import os
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import db_manager
from app.services.extraction.metrics_processor import process_metrics


async def run_manual_extraction():
    """Run metrics extraction manually"""
    
    print("=" * 100)
    print("🔧 MANUAL METRICS EXTRACTION")
    print("=" * 100)
    
    # Connect to database
    print("\n🔗 Connecting to database...")
    await db_manager.connect()
    pool = db_manager.get_pool()
    
    try:
        # Run extraction with different batch sizes
        batch_sizes = [50, 100, 200]
        
        for batch_size in batch_sizes:
            print(f"\n{'─' * 100}")
            print(f"🔄 Running extraction with batch_size={batch_size}")
            print(f"{'─' * 100}")
            
            result = await process_metrics(pool, batch_size=batch_size)
            
            print(f"✅ Processed: {result['processed_events']} events")
            print(f"✅ Created: {result['metrics_created']} metrics")
            
            if result['processed_events'] == 0:
                print("⚠️  No events found to process")
                break
            
            if result['metrics_created'] == 0:
                print("⚠️  No metrics extracted from events")
        
        # Show final statistics
        print(f"\n{'=' * 100}")
        print("📊 FINAL STATISTICS")
        print(f"{'=' * 100}")
        
        async with pool.acquire() as conn:
            total_metrics = await conn.fetchval("SELECT COUNT(*) FROM event_metrics")
            total_events = await conn.fetchval("SELECT COUNT(*) FROM news_events")
            events_with_metrics = await conn.fetchval(
                """
                SELECT COUNT(DISTINCT event_id) FROM event_metrics
                """
            )
            
            print(f"Total metrics in DB: {total_metrics}")
            print(f"Total events in DB: {total_events}")
            print(f"Events with metrics: {events_with_metrics}")
            print(f"Coverage: {(events_with_metrics / total_events * 100):.1f}%")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(run_manual_extraction())
