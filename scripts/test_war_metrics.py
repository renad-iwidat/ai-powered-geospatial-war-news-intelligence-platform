"""
Test metrics extraction on war-related news
"""
import asyncio
import asyncpg
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, '.')
from app.services.extraction.metrics_extractor import extract_metrics

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Get war-related events
    result = await conn.fetch("""
        SELECT 
            ne.id,
            COALESCE(t.content, rn.content_original) AS content
        FROM news_events ne
        JOIN raw_news rn ON rn.id = ne.raw_news_id
        LEFT JOIN translations t ON t.raw_news_id = rn.id
        WHERE ne.id IN (195, 200, 201, 204, 214, 217)
        LIMIT 5
    """)
    
    print("=" * 80)
    print("Testing Metrics Extraction on War News")
    print("=" * 80)
    
    for r in result:
        content = r['content'] or ""
        
        print(f"\nEvent {r['id']}:")
        print(content[:300])
        print("-" * 80)
        
        metrics = extract_metrics(content)
        
        if metrics:
            print(f"✅ Found {len(metrics)} metrics:")
            for m in metrics:
                print(f"  - {m['metric_type']}: {m['value']}")
        else:
            print("❌ No metrics found")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
