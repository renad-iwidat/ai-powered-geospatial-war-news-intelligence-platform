#!/usr/bin/env python3
"""
Test script to verify logging output from data processing pipeline
Run this to see the enhanced logging in action
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging to show all levels
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_logging():
    """Test the logging output"""
    from app.core.database import get_db_pool
    from app.services.geo.location_processor import process_locations
    from app.services.extraction.metrics_processor import process_metrics
    from app.core.config import settings
    import asyncpg
    
    print("\n" + "="*80)
    print("TESTING DATA PROCESSING PIPELINE LOGGING")
    print("="*80 + "\n")
    
    # Create connection pool
    try:
        pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=1,
            max_size=2,
            command_timeout=120
        )
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print(f"   DATABASE_URL: {settings.DATABASE_URL}")
        return
    
    try:
        # Test location extraction
        print("\n" + "-"*80)
        print("TEST 1: Location Extraction Logging")
        print("-"*80 + "\n")
        
        location_result = await process_locations(pool, batch_size=10)
        print(f"\n✅ Location extraction result: {location_result}\n")
        
        # Test metrics extraction
        print("\n" + "-"*80)
        print("TEST 2: Metrics Extraction Logging")
        print("-"*80 + "\n")
        
        metrics_result = await process_metrics(pool, batch_size=20)
        print(f"\n✅ Metrics extraction result: {metrics_result}\n")
        
        print("\n" + "="*80)
        print("✅ LOGGING TEST COMPLETED SUCCESSFULLY")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(test_logging())
