import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    pool = await asyncpg.create_pool(os.getenv('DATABASE_URL'))
    
    async with pool.acquire() as conn:
        # Get view columns
        result = await conn.fetch('SELECT * FROM vw_news_ar_feed LIMIT 1')
        
        if result:
            print("View columns:")
            for key in result[0].keys():
                print(f"  - {key}")
        else:
            print("No data in view")
    
    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
