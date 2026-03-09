#!/usr/bin/env python3
"""
View News Articles with Metrics Details
عرض الأخبار مع تفاصيل المؤشرات
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import db_manager


async def view_metrics_details():
    """View news articles with metrics"""
    
    print("=" * 100)
    print("📰 NEWS ARTICLES WITH METRICS DETAILS")
    print("=" * 100)
    
    # Connect to database
    print("\n🔗 Connecting to database...")
    await db_manager.connect()
    pool = db_manager.get_pool()
    
    try:
        async with pool.acquire() as conn:
            # Get articles with metrics
            print("\n📊 Fetching articles with metrics...\n")
            
            rows = await conn.fetch(
                """
                SELECT 
                    rn.id as article_id,
                    rn.title_original,
                    rn.published_at,
                    rn.fetched_at,
                    COUNT(DISTINCT ne.id) as event_count,
                    COUNT(DISTINCT em.id) as metric_count,
                    STRING_AGG(DISTINCT em.metric_type, ', ') as metric_types,
                    STRING_AGG(DISTINCT em.value::text, ', ') as metric_values
                FROM raw_news rn
                LEFT JOIN news_events ne ON ne.raw_news_id = rn.id
                LEFT JOIN event_metrics em ON em.event_id = ne.id
                WHERE em.id IS NOT NULL
                GROUP BY rn.id, rn.title_original, rn.published_at, rn.fetched_at
                ORDER BY rn.published_at DESC NULLS LAST
                LIMIT 20
                """
            )
            
            if not rows:
                print("❌ No articles with metrics found")
                return
            
            print(f"✅ Found {len(rows)} articles with metrics\n")
            
            for idx, row in enumerate(rows, 1):
                print(f"{'─' * 100}")
                print(f"📄 Article {idx}/{len(rows)}")
                print(f"{'─' * 100}")
                
                article_id = row['article_id']
                title = row['title_original']
                published_at = row['published_at']
                fetched_at = row['fetched_at']
                event_count = row['event_count']
                metric_count = row['metric_count']
                metric_types = row['metric_types']
                metric_values = row['metric_values']
                
                print(f"Article ID: {article_id}")
                print(f"Title: {title}")
                print(f"Published: {published_at if published_at else 'Unknown'}")
                print(f"Fetched: {fetched_at if fetched_at else 'Unknown'}")
                print(f"Events: {event_count}")
                print(f"Metrics: {metric_count}")
                print(f"Metric Types: {metric_types}")
                print(f"Metric Values: {metric_values}")
                
                # Get detailed metrics for this article
                print(f"\n   📋 Detailed Metrics:")
                metrics = await conn.fetch(
                    """
                    SELECT 
                        em.id as metric_id,
                        em.metric_type,
                        em.value,
                        em.snippet,
                        em.created_at,
                        ne.place_name
                    FROM event_metrics em
                    JOIN news_events ne ON ne.id = em.event_id
                    WHERE ne.raw_news_id = $1
                    ORDER BY em.created_at DESC
                    """,
                    article_id
                )
                
                for m in metrics:
                    print(f"      • ID: {m['metric_id']}")
                    print(f"        Type: {m['metric_type']}")
                    print(f"        Value: {m['value']}")
                    print(f"        Place: {m['place_name']}")
                    print(f"        Created: {m['created_at']}")
                    print(f"        Snippet: {m['snippet'][:80]}...")
                    print()
            
            # Summary statistics
            print(f"\n{'=' * 100}")
            print("📊 SUMMARY STATISTICS")
            print(f"{'=' * 100}")
            
            total_articles = await conn.fetchval("SELECT COUNT(*) FROM raw_news")
            articles_with_metrics = await conn.fetchval(
                """
                SELECT COUNT(DISTINCT rn.id)
                FROM raw_news rn
                JOIN news_events ne ON ne.raw_news_id = rn.id
                JOIN event_metrics em ON em.event_id = ne.id
                """
            )
            total_metrics = await conn.fetchval("SELECT COUNT(*) FROM event_metrics")
            
            print(f"Total articles: {total_articles}")
            print(f"Articles with metrics: {articles_with_metrics}")
            print(f"Coverage: {(articles_with_metrics / total_articles * 100):.1f}%")
            print(f"Total metrics: {total_metrics}")
            print(f"Average metrics per article: {(total_metrics / articles_with_metrics):.1f}" if articles_with_metrics > 0 else "N/A")
            
            # Metric types distribution
            print(f"\n📈 Metric Types Distribution:")
            print(f"{'─' * 100}")
            
            metric_dist = await conn.fetch(
                """
                SELECT 
                    metric_type,
                    COUNT(*) as count,
                    MIN(value) as min_value,
                    MAX(value) as max_value,
                    AVG(value)::int as avg_value,
                    MIN(created_at) as first_created,
                    MAX(created_at) as last_created
                FROM event_metrics
                GROUP BY metric_type
                ORDER BY count DESC
                """
            )
            
            for m in metric_dist:
                print(f"\n{m['metric_type']}:")
                print(f"  Count: {m['count']}")
                print(f"  Range: {m['min_value']} - {m['max_value']}")
                print(f"  Average: {m['avg_value']}")
                print(f"  First: {m['first_created']}")
                print(f"  Last: {m['last_created']}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(view_metrics_details())
