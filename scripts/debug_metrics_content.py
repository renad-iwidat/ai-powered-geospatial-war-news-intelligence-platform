#!/usr/bin/env python3
"""
Debug Metrics Content
تحقق من الـ content اللي بتقرأه الـ metrics extraction
"""

import sys
import os
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import db_manager
from app.services.extraction.metrics_extractor import extract_metrics


async def debug_metrics_content():
    """Debug metrics extraction content"""
    
    print("=" * 100)
    print("🔍 DEBUG METRICS EXTRACTION CONTENT")
    print("=" * 100)
    
    # Connect to database
    print("\n🔗 Connecting to database...")
    await db_manager.connect()
    pool = db_manager.get_pool()
    
    try:
        async with pool.acquire() as conn:
            # Get events with content
            print("\n📊 Fetching events with content...\n")
            
            rows = await conn.fetch(
                """
                SELECT
                    ne.id AS event_id,
                    ne.place_name,
                    rn.id as article_id,
                    rn.title_original,
                    rn.has_numbers,
                    COALESCE(t.content, rn.content_original) AS content,
                    LENGTH(COALESCE(t.content, rn.content_original)) as content_length,
                    CASE WHEN t.content IS NOT NULL THEN 'translation' ELSE 'raw_news' END as source
                FROM news_events ne
                JOIN raw_news rn ON rn.id = ne.raw_news_id
                LEFT JOIN translations t ON t.raw_news_id = rn.id
                WHERE rn.has_numbers = true
                AND (
                    (t.content IS NOT NULL AND LENGTH(t.content) > 50)
                    OR (rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 50)
                )
                AND NOT EXISTS (
                    SELECT 1
                    FROM event_metrics em
                    WHERE em.event_id = ne.id
                )
                LIMIT 5
                """
            )
            
            if not rows:
                print("❌ No events found")
                return
            
            print(f"✅ Found {len(rows)} events\n")
            
            for idx, row in enumerate(rows, 1):
                print(f"{'─' * 100}")
                print(f"Event {idx}/{len(rows)}")
                print(f"{'─' * 100}")
                
                event_id = row['event_id']
                article_id = row['article_id']
                place = row['place_name']
                title = row['title_original']
                has_numbers = row['has_numbers']
                content = row['content']
                content_length = row['content_length']
                source = row['source']
                
                print(f"Event ID: {event_id}")
                print(f"Article ID: {article_id}")
                print(f"Place: {place}")
                print(f"Title: {title[:80]}...")
                print(f"Has Numbers: {has_numbers}")
                print(f"Source: {source}")
                print(f"Content Length: {content_length}")
                print(f"\nContent Preview:")
                print(f"{content[:300]}...")
                
                # Try extraction
                print(f"\n🔎 Extracting metrics...")
                metrics = extract_metrics(content)
                
                if metrics:
                    print(f"✅ Found {len(metrics)} metrics:")
                    for m in metrics:
                        print(f"   • {m['metric_type']}: {m['value']}")
                        print(f"     Snippet: {m['snippet'][:80]}...")
                else:
                    print(f"❌ No metrics found")
                    
                    # Debug: show what patterns would match
                    print(f"\n🔍 Debug Info:")
                    
                    # Check for numbers
                    import re
                    numbers = re.findall(r'\d+', content)
                    if numbers:
                        print(f"   Numbers found: {numbers[:10]}")
                    else:
                        print(f"   No numbers found in content")
                    
                    # Check for Arabic keywords
                    keywords = ['قتل', 'جرح', 'صاروخ', 'طائرة', 'غارة', 'ألف', 'مليون']
                    found_keywords = [kw for kw in keywords if kw in content]
                    if found_keywords:
                        print(f"   Keywords found: {found_keywords}")
                    else:
                        print(f"   No keywords found")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(debug_metrics_content())
