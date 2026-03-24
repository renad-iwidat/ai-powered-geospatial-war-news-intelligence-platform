#!/usr/bin/env python3
"""
Cleanup Excluded Sources
حذف الأحداث من المصادر 17 و 18 (مصادر النهار)
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
import asyncpg


async def cleanup():
    """Delete events from excluded sources"""
    print("\n" + "="*80)
    print("CLEANUP: Deleting events from excluded sources (17 & 18)")
    print("="*80 + "\n")
    
    try:
        pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=1,
            max_size=2,
            command_timeout=120
        )
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False
    
    try:
        async with pool.acquire() as conn:
            # Count events before deletion
            before = await conn.fetchval(
                "SELECT COUNT(*) FROM news_events WHERE raw_news_id IN (SELECT id FROM raw_news WHERE source_id IN (17, 18))"
            )
            
            print(f"📊 Events from sources 17 & 18 before cleanup: {before}\n")
            
            if before == 0:
                print("✅ No events to delete\n")
                return True
            
            # Delete events from sources 17 & 18
            print("🗑️  Deleting events...")
            await conn.execute(
                "DELETE FROM news_events WHERE raw_news_id IN (SELECT id FROM raw_news WHERE source_id IN (17, 18))"
            )
            
            print(f"✅ Deleted {before} events\n")
            
            # Verify
            after = await conn.fetchval(
                "SELECT COUNT(*) FROM news_events WHERE raw_news_id IN (SELECT id FROM raw_news WHERE source_id IN (17, 18))"
            )
            
            print(f"📊 Events from sources 17 & 18 after cleanup: {after}\n")
            
            if after == 0:
                print("✅ Cleanup successful!\n")
                return True
            else:
                print(f"❌ Still {after} events remaining\n")
                return False
    
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await pool.close()


if __name__ == "__main__":
    success = asyncio.run(cleanup())
    sys.exit(0 if success else 1)
