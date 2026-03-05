"""
Test metrics extraction on real content
"""
import asyncio
import asyncpg
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.extraction.metrics_extractor import extract_metrics

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Get sample content
    result = await conn.fetch("""
        SELECT 
            ne.id,
            COALESCE(t.content, rn.content_original) AS content
        FROM news_events ne
        JOIN raw_news rn ON rn.id = ne.raw_news_id
        LEFT JOIN translations t ON t.raw_news_id = rn.id
        WHERE (
            (t.content IS NOT NULL AND LENGTH(t.content) > 100)
            OR (rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 100)
        )
        AND NOT EXISTS (
            SELECT 1 FROM event_metrics em WHERE em.event_id = ne.id
        )
        LIMIT 10
    """)
    
    print("=" * 80)
    print("Testing Metrics Extraction on Real Content")
    print("=" * 80)
    
    for i, r in enumerate(result, 1):
        content = r['content'] or ""
        
        print(f"\n{'=' * 80}")
        print(f"Event {i} (ID: {r['id']})")
        print(f"{'=' * 80}")
        print(f"Content preview (first 500 chars):")
        print(content[:500])
        print(f"\n{'-' * 80}")
        
        # Extract metrics
        metrics = extract_metrics(content)
        
        if metrics:
            print(f"✅ Found {len(metrics)} metrics:")
            for m in metrics:
                print(f"  - {m['metric_type']}: {m['value']}")
                print(f"    Snippet: {m['snippet'][:100]}...")
        else:
            print("❌ No metrics found")
            
            # Check if content has numbers
            import re
            numbers = re.findall(r'\d+', content)
            if numbers:
                print(f"⚠️  Content has {len(numbers)} numbers: {numbers[:10]}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
