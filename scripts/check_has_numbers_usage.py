"""
Check has_numbers column usage
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    print("=" * 80)
    print("HAS_NUMBERS COLUMN ANALYSIS:")
    print("=" * 80)
    
    # Check distribution
    result = await conn.fetchrow("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN has_numbers = true THEN 1 END) as with_numbers,
            COUNT(CASE WHEN has_numbers = false THEN 1 END) as without_numbers
        FROM raw_news
    """)
    
    print(f"\nTotal news: {result['total']}")
    print(f"With numbers (has_numbers=true): {result['with_numbers']} ({result['with_numbers']/result['total']*100:.1f}%)")
    print(f"Without numbers (has_numbers=false): {result['without_numbers']} ({result['without_numbers']/result['total']*100:.1f}%)")
    
    # Check events with has_numbers
    events_stats = await conn.fetchrow("""
        SELECT 
            COUNT(*) as total_events,
            COUNT(CASE WHEN rn.has_numbers = true THEN 1 END) as events_with_numbers,
            COUNT(CASE WHEN (t.content IS NOT NULL AND LENGTH(t.content) > 50) OR (rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 50) THEN 1 END) as events_with_content,
            COUNT(CASE WHEN rn.has_numbers = true AND ((t.content IS NOT NULL AND LENGTH(t.content) > 50) OR (rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 50)) THEN 1 END) as events_with_numbers_and_content
        FROM news_events ne
        JOIN raw_news rn ON rn.id = ne.raw_news_id
        LEFT JOIN translations t ON t.raw_news_id = rn.id
    """)
    
    print("\n" + "=" * 80)
    print("EVENTS ANALYSIS:")
    print("=" * 80)
    print(f"Total events: {events_stats['total_events']}")
    print(f"Events from news with numbers: {events_stats['events_with_numbers']}")
    print(f"Events with content: {events_stats['events_with_content']}")
    print(f"Events with numbers AND content: {events_stats['events_with_numbers_and_content']}")
    
    # Check if using has_numbers would improve performance
    print("\n" + "=" * 80)
    print("PERFORMANCE IMPACT:")
    print("=" * 80)
    
    current_query = events_stats['events_with_content']
    optimized_query = events_stats['events_with_numbers_and_content']
    
    print(f"Current query processes: {current_query} events")
    print(f"With has_numbers filter: {optimized_query} events")
    print(f"Reduction: {current_query - optimized_query} events ({(current_query - optimized_query)/current_query*100:.1f}%)")
    
    # Check metrics extraction success rate
    metrics_count = await conn.fetchval("SELECT COUNT(*) FROM event_metrics")
    
    print("\n" + "=" * 80)
    print("METRICS EXTRACTION SUCCESS RATE:")
    print("=" * 80)
    print(f"Metrics extracted: {metrics_count}")
    print(f"From {current_query} events with content: {metrics_count/current_query*100:.1f}% success rate")
    print(f"From {optimized_query} events with numbers: {metrics_count/optimized_query*100:.1f}% success rate")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
