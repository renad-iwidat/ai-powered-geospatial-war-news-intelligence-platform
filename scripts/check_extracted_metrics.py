"""
Check extracted metrics
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Get metrics summary
    print("=" * 80)
    print("Extracted Metrics Summary:")
    print("=" * 80)
    
    result = await conn.fetch("""
        SELECT 
            metric_type,
            COUNT(*) as count,
            SUM(value) as total_value,
            AVG(value) as avg_value
        FROM event_metrics
        GROUP BY metric_type
        ORDER BY count DESC
    """)
    
    for r in result:
        print(f"\n{r['metric_type']}:")
        print(f"  Count: {r['count']}")
        print(f"  Total: {r['total_value']}")
        print(f"  Average: {r['avg_value']:.1f}")
    
    # Get sample metrics
    print("\n" + "=" * 80)
    print("Sample Metrics:")
    print("=" * 80)
    
    result2 = await conn.fetch("""
        SELECT 
            em.metric_type,
            em.value,
            em.snippet,
            ne.place_name
        FROM event_metrics em
        JOIN news_events ne ON ne.id = em.event_id
        ORDER BY em.created_at DESC
        LIMIT 10
    """)
    
    for r in result2:
        print(f"\n{r['metric_type']}: {r['value']}")
        print(f"  Location: {r['place_name']}")
        print(f"  Snippet: {r['snippet'][:100]}...")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
