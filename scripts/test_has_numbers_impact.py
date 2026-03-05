"""
Test impact of has_numbers filter
"""
import asyncio
import asyncpg
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, '.')
from app.services.extraction.metrics_processor import process_metrics

load_dotenv()

async def main():
    pool = await asyncpg.create_pool(os.getenv('DATABASE_URL'))
    
    print("=" * 80)
    print("TESTING HAS_NUMBERS FILTER IMPACT")
    print("=" * 80)
    
    # Test with new query (has_numbers = true)
    print("\nProcessing with has_numbers filter...")
    result = await process_metrics(pool, batch_size=50)
    
    print(f"\n✅ Processed: {result['processed_events']} events")
    print(f"✅ Extracted: {result['metrics_created']} metrics")
    
    if result['processed_events'] > 0:
        success_rate = (result['metrics_created'] / result['processed_events']) * 100
        print(f"✅ Success rate: {success_rate:.1f}%")
    
    # Check what we got
    conn = await pool.acquire()
    
    metrics_by_type = await conn.fetch("""
        SELECT metric_type, COUNT(*) as count, SUM(value) as total
        FROM event_metrics
        GROUP BY metric_type
        ORDER BY count DESC
    """)
    
    print("\n" + "=" * 80)
    print("EXTRACTED METRICS BY TYPE:")
    print("=" * 80)
    for m in metrics_by_type:
        print(f"  {m['metric_type']}: {m['count']} metrics (total: {m['total']})")
    
    # Check if we missed any important events
    print("\n" + "=" * 80)
    print("CHECKING FOR MISSED EVENTS:")
    print("=" * 80)
    
    # Events without has_numbers but with war keywords
    missed = await conn.fetch("""
        SELECT 
            ne.id,
            rn.title_original,
            COALESCE(t.content, rn.content_original) as content
        FROM news_events ne
        JOIN raw_news rn ON rn.id = ne.raw_news_id
        LEFT JOIN translations t ON t.raw_news_id = rn.id
        WHERE rn.has_numbers = false
        AND (
            (t.content IS NOT NULL AND LENGTH(t.content) > 50)
            OR (rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 50)
        )
        AND (
            COALESCE(t.content, rn.content_original) LIKE '%صاروخ%'
            OR COALESCE(t.content, rn.content_original) LIKE '%قتل%'
            OR COALESCE(t.content, rn.content_original) LIKE '%مقتل%'
            OR COALESCE(t.content, rn.content_original) LIKE '%اصابة%'
            OR COALESCE(t.content, rn.content_original) LIKE '%مسيرة%'
        )
        LIMIT 5
    """)
    
    if missed:
        print(f"\n⚠️  Found {len(missed)} events with war keywords but has_numbers=false:")
        for m in missed:
            print(f"\nEvent {m['id']}: {m['title_original'][:60]}")
            # Try to extract metrics manually
            from app.services.extraction.metrics_extractor import extract_metrics
            metrics = extract_metrics(m['content'] or "")
            if metrics:
                print(f"  ⚠️  WOULD HAVE EXTRACTED: {len(metrics)} metrics!")
                for metric in metrics[:3]:
                    print(f"    - {metric['metric_type']}: {metric['value']}")
            else:
                print(f"  ✅ Correctly filtered (no metrics)")
    else:
        print("\n✅ No important events missed!")
    
    await conn.close()
    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
