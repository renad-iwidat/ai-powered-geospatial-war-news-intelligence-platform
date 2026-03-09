#!/usr/bin/env python3
"""
Clean up fallback forecasts from the database
Removes any forecasts that contain error messages (fallback responses)
"""

import asyncio
import asyncpg
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


async def cleanup_fallback_forecasts():
    """Remove fallback forecasts from database"""
    
    print("=" * 70)
    print("🧹 Cleaning up fallback forecasts from database")
    print("=" * 70)
    
    try:
        # Connect to database
        pool = await asyncpg.create_pool(settings.DATABASE_URL)
        
        async with pool.acquire() as conn:
            # Get all forecasts
            query = """
                SELECT id, forecast_type, forecast_data, generated_at
                FROM ai_forecasts
                ORDER BY generated_at DESC
            """
            
            rows = await conn.fetch(query)
            
            print(f"\n📊 Found {len(rows)} forecasts in database\n")
            
            fallback_count = 0
            
            for row in rows:
                forecast_id = row['id']
                forecast_type = row['forecast_type']
                generated_at = row['generated_at']
                
                # Parse forecast data
                forecast_data = json.loads(row['forecast_data']) if isinstance(row['forecast_data'], str) else row['forecast_data']
                
                # Check if it's a fallback response (has 'error' field)
                if 'error' in forecast_data:
                    print(f"❌ ID {forecast_id} ({forecast_type}) - {generated_at}")
                    print(f"   Error: {forecast_data['error'][:80]}...")
                    
                    # Delete this forecast
                    delete_query = "DELETE FROM ai_forecasts WHERE id = $1"
                    await conn.execute(delete_query, forecast_id)
                    fallback_count += 1
                else:
                    print(f"✅ ID {forecast_id} ({forecast_type}) - {generated_at}")
                    print(f"   Trend: {forecast_data.get('overall_trend', 'N/A')}")
            
            print(f"\n{'=' * 70}")
            print(f"🧹 Deleted {fallback_count} fallback forecasts")
            print(f"✅ Cleanup completed successfully")
            print(f"{'=' * 70}\n")
        
        await pool.close()
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(cleanup_fallback_forecasts())
