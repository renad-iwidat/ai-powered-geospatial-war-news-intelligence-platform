"""
Find news with war-related keywords
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Find events with war keywords
    result = await conn.fetch("""
        SELECT 
            ne.id,
            COALESCE(t.content, rn.content_original) AS content
        FROM news_events ne
        JOIN raw_news rn ON rn.id = ne.raw_news_id
        LEFT JOIN translations t ON t.raw_news_id = rn.id
        WHERE (
            COALESCE(t.content, rn.content_original) LIKE '%صاروخ%'
            OR COALESCE(t.content, rn.content_original) LIKE '%قتل%'
            OR COALESCE(t.content, rn.content_original) LIKE '%غارة%'
            OR COALESCE(t.content, rn.content_original) LIKE '%قصف%'
            OR COALESCE(t.content, rn.content_original) LIKE '%مقتل%'
            OR COALESCE(t.content, rn.content_original) LIKE '%ضربة%'
        )
        LIMIT 10
    """)
    
    print(f"Found {len(result)} events with war-related keywords\n")
    
    for r in result:
        print(f"Event {r['id']}:")
        content = r['content'] or ""
        print(content[:300])
        print("-" * 80)
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
