"""
Check metrics extraction status
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Check has_numbers distribution
    print("=" * 60)
    print("has_numbers Distribution:")
    print("=" * 60)
    result = await conn.fetch(
        'SELECT has_numbers, COUNT(*) as count FROM raw_news GROUP BY has_numbers'
    )
    for r in result:
        print(f"  {r['has_numbers']}: {r['count']}")
    
    # Check events ready for metrics extraction
    print("\n" + "=" * 60)
    print("Events Ready for Metrics Extraction:")
    print("=" * 60)
    result2 = await conn.fetch("""
        SELECT COUNT(*) as count 
        FROM news_events ne 
        JOIN raw_news rn ON rn.id = ne.raw_news_id 
        WHERE rn.has_numbers = true 
        AND NOT EXISTS (
            SELECT 1 FROM event_metrics em WHERE em.event_id = ne.id
        )
    """)
    print(f"  Ready: {result2[0]['count']}")
    
    # Check total events without metrics
    print("\n" + "=" * 60)
    print("Events Without Metrics (regardless of has_numbers):")
    print("=" * 60)
    result3 = await conn.fetch("""
        SELECT COUNT(*) as count 
        FROM news_events ne 
        WHERE NOT EXISTS (
            SELECT 1 FROM event_metrics em WHERE em.event_id = ne.id
        )
    """)
    print(f"  Total: {result3[0]['count']}")
    
    # Sample content from events without metrics
    print("\n" + "=" * 60)
    print("Sample Content (first 3 events without metrics):")
    print("=" * 60)
    result4 = await conn.fetch("""
        SELECT 
            ne.id,
            rn.has_numbers,
            COALESCE(t.content, rn.content_original) AS content
        FROM news_events ne
        JOIN raw_news rn ON rn.id = ne.raw_news_id
        LEFT JOIN translations t ON t.raw_news_id = rn.id
        WHERE NOT EXISTS (
            SELECT 1 FROM event_metrics em WHERE em.event_id = ne.id
        )
        LIMIT 3
    """)
    
    for i, r in enumerate(result4, 1):
        print(f"\n--- Event {i} (ID: {r['id']}, has_numbers: {r['has_numbers']}) ---")
        content = r['content'] or ""
        print(content[:300] + "..." if len(content) > 300 else content)
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
