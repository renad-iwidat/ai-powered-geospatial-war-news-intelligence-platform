"""
Process all events to extract metrics
"""
import asyncio
import asyncpg
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.extraction.metrics_processor import process_metrics

load_dotenv()

async def main():
    # Create connection pool
    pool = await asyncpg.create_pool(os.getenv('DATABASE_URL'))
    
    print("=" * 60)
    print("Starting Metrics Extraction")
    print("=" * 60)
    
    total_processed = 0
    total_metrics = 0
    batch_num = 0
    
    while True:
        batch_num += 1
        print(f"\n--- Batch #{batch_num} ---")
        
        result = await process_metrics(pool, batch_size=30)
        
        processed = result['processed_events']
        metrics = result['metrics_created']
        
        total_processed += processed
        total_metrics += metrics
        
        print(f"✅ Events processed: {processed}")
        print(f"✅ Metrics extracted: {metrics}")
        
        if processed == 0:
            print("\n✅ All events processed!")
            break
        
        # Small delay between batches
        await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("Final Statistics:")
    print("=" * 60)
    print(f"Total events processed: {total_processed}")
    print(f"Total metrics extracted: {total_metrics}")
    
    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
