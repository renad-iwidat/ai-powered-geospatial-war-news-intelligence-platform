"""
Check content length for recent Arabic news
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    print("=" * 80)
    print("RECENT ARABIC NEWS CONTENT LENGTH:")
    print("=" * 80)
    
    result = await conn.fetch("""
        SELECT 
            id, 
            title_original,
            LENGTH(content_original) as content_len,
            CASE 
                WHEN content_original IS NULL THEN 'NULL'
                WHEN LENGTH(content_original) = 0 THEN 'EMPTY'
                WHEN LENGTH(content_original) < 100 THEN 'TOO SHORT'
                ELSE 'OK'
            END as status
        FROM raw_news 
        WHERE id >= 380 AND language_id = 1 
        ORDER BY id DESC
    """)
    
    for r in result:
        print(f"ID {r['id']}: {r['status']:10} | Length: {r['content_len'] or 0:5} | {r['title_original'][:60]}")
    
    # Summary
    ok_count = sum(1 for r in result if r['status'] == 'OK')
    problem_count = len(result) - ok_count
    
    print(f"\nSummary: {ok_count} OK, {problem_count} with problems")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
