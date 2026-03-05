"""
Check unprocessed events with actual content
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Check events with content but no metrics
    print("=" * 60)
    print("Events with Content but No Metrics:")
    print("=" * 60)
    result = await conn.fetch("""
        SELECT COUNT(*) as count 
        FROM news_events ne 
        JOIN raw_news rn ON rn.id = ne.raw_news_id 
        LEFT JOIN translations t ON t.raw_news_id = rn.id
        WHERE (
            (t.content IS NOT NULL AND LENGTH(t.content) > 50)
            OR (rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 50)
        )
        AND NOT EXISTS (
            SELECT 1 FROM event_metrics em WHERE em.event_id = ne.id
        )
    """)
    print(f"  Total: {result[0]['count']}")
    
    # Sample with actual content
    print("\n" + "=" * 60)
    print("Sample Events with Content:")
    print("=" * 60)
    result2 = await conn.fetch("""
        SELECT 
            ne.id,
            rn.has_numbers,
            LENGTH(COALESCE(t.content, rn.content_original)) as content_length,
            COALESCE(t.content, rn.content_original) AS content
        FROM news_events ne
        JOIN raw_news rn ON rn.id = ne.raw_news_id
        LEFT JOIN translations t ON t.raw_news_id = rn.id
        WHERE (
            (t.content IS NOT NULL AND LENGTH(t.content) > 50)
            OR (rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 50)
        )
        AND NOT EXISTS (
            SELECT 1 FROM event_metrics em WHERE em.event_id = ne.id
        )
        LIMIT 5
    """)
    
    for i, r in enumerate(result2, 1):
        print(f"\n--- Event {i} (ID: {r['id']}, has_numbers: {r['has_numbers']}, length: {r['content_length']}) ---")
        content = r['content'] or ""
        print(content[:400] + "..." if len(content) > 400 else content)
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
