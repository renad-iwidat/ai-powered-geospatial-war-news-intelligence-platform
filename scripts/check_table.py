import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def check():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Check if table exists
    exists = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'ai_forecasts'
        )
    """)
    
    print(f"Table 'ai_forecasts' exists: {exists}")
    
    if exists:
        # Get columns
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'ai_forecasts' 
            ORDER BY ordinal_position
        """)
        
        print("\nColumns:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']}")
        
        # Count rows
        count = await conn.fetchval("SELECT COUNT(*) FROM ai_forecasts")
        print(f"\nRows in table: {count}")
    
    await conn.close()

asyncio.run(check())
