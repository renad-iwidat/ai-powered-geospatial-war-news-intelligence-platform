#!/usr/bin/env python3
"""
Run database migration
"""
import asyncio
import asyncpg
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings


async def run_migration(migration_file: str):
    """Run a SQL migration file"""
    
    print(f"🔄 Running migration: {migration_file}")
    
    # Read migration file
    migration_path = Path(__file__).parent / "migrations" / migration_file
    
    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_path}")
        return False
    
    with open(migration_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Connect and execute
    try:
        conn = await asyncpg.connect(dsn=settings.DATABASE_URL)
        
        await conn.execute(sql)
        
        print(f"✅ Migration completed successfully!")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all pending migrations"""
    
    print("=" * 80)
    print("🚀 Database Migration Runner")
    print("=" * 80)
    
    migrations = [
        "001_create_ai_forecasts_table.sql"
    ]
    
    for migration in migrations:
        success = await run_migration(migration)
        if not success:
            print(f"\n❌ Stopped at failed migration: {migration}")
            sys.exit(1)
        print()
    
    print("=" * 80)
    print("✅ All migrations completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
