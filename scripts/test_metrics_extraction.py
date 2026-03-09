#!/usr/bin/env python3
"""
Test Metrics Extraction on Existing News
استخراج المؤشرات من الأخبار الموجودة في قاعدة البيانات
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import db_manager
from app.services.extraction.metrics_extractor import extract_metrics


async def test_metrics_extraction():
    """Test metrics extraction on existing news"""
    
    print("=" * 70)
    print("🔍 Testing Metrics Extraction on Existing News")
    print("=" * 70)
    
    # Connect to database first
    print("\n🔗 Connecting to database...")
    await db_manager.connect()
    
    # Get database pool
    pool = db_manager.get_pool()
    
    try:
        async with pool.acquire() as conn:
            # Get news articles with content
            print("\n📰 Fetching news articles with content...")
            rows = await conn.fetch(
                """
                SELECT 
                    rn.id,
                    rn.title_original,
                    COALESCE(t.content, rn.content_original) as content,
                    rn.language_id,
                    l.code as language_code
                FROM raw_news rn
                LEFT JOIN translations t ON t.raw_news_id = rn.id
                LEFT JOIN languages l ON rn.language_id = l.id
                WHERE COALESCE(t.content, rn.content_original) IS NOT NULL
                AND LENGTH(COALESCE(t.content, rn.content_original)) > 50
                LIMIT 10
                """
            )
            
            if not rows:
                print("❌ No news articles found in database")
                return
            
            print(f"✅ Found {len(rows)} news articles\n")
            
            # Test extraction on each article
            total_metrics = 0
            for idx, row in enumerate(rows, 1):
                print(f"\n{'─' * 70}")
                print(f"📄 Article {idx}/{len(rows)}")
                print(f"{'─' * 70}")
                print(f"ID: {row['id']}")
                print(f"Language: {row['language_code']}")
                print(f"Title: {row['title_original'][:100]}...")
                
                # Extract metrics
                content = row['content'] or ""
                print(f"\nContent Preview: {content[:200]}...")
                
                metrics = extract_metrics(content)
                
                if metrics:
                    print(f"\n✅ Found {len(metrics)} metrics:")
                    for m in metrics:
                        print(f"   • {m['metric_type']}: {m['value']}")
                        print(f"     Snippet: {m['snippet'][:100]}...")
                    total_metrics += len(metrics)
                else:
                    print("\n⚠️  No metrics found in this article")
            
            print(f"\n{'=' * 70}")
            print(f"📊 Summary: Found {total_metrics} total metrics")
            print(f"{'=' * 70}")
            
            # Show database statistics
            print("\n📈 Database Statistics:")
            
            # Count articles
            article_count = await conn.fetchval("SELECT COUNT(*) FROM raw_news")
            print(f"   • Total articles: {article_count}")
            
            # Count events
            event_count = await conn.fetchval("SELECT COUNT(*) FROM news_events")
            print(f"   • Total events: {event_count}")
            
            # Count metrics
            metric_count = await conn.fetchval("SELECT COUNT(*) FROM event_metrics")
            print(f"   • Total metrics in DB: {metric_count}")
            
            # Count events without metrics
            events_without_metrics = await conn.fetchval(
                """
                SELECT COUNT(DISTINCT ne.id) 
                FROM news_events ne
                WHERE NOT EXISTS (
                    SELECT 1 FROM event_metrics em WHERE em.event_id = ne.id
                )
                """
            )
            print(f"   • Events without metrics: {events_without_metrics}")
            
            # Show metric types distribution
            print("\n📊 Metrics Distribution in Database:")
            metric_types = await conn.fetch(
                """
                SELECT metric_type, COUNT(*) as count
                FROM event_metrics
                GROUP BY metric_type
                ORDER BY count DESC
                """
            )
            
            if metric_types:
                for mt in metric_types:
                    print(f"   • {mt['metric_type']}: {mt['count']}")
            else:
                print("   • No metrics in database yet")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(test_metrics_extraction())
