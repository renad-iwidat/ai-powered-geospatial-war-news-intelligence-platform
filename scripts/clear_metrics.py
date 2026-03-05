"""
Clear all metrics from database
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    result = await conn.execute('DELETE FROM event_metrics')
    print(f"✅ Cleared all metrics: {result}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
