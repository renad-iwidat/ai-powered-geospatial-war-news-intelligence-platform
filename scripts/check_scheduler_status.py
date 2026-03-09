#!/usr/bin/env python3
"""
Check Scheduler Status and Processing History
تحقق من حالة الـ scheduler والمعالجة
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import db_manager


async def check_scheduler_status():
    """Check scheduler processing status"""
    
    print("=" * 100)
    print("🔍 SCHEDULER STATUS CHECK")
    print("=" * 100)
    
    # Connect to database
    print("\n🔗 Connecting to database...")
    await db_manager.connect()
    pool = db_manager.get_pool()
    
    try:
        async with pool.acquire() as conn:
            # Check articles by date
            print("\n📅 Articles by Date:")
            print("─" * 100)
            
            articles_by_date = await conn.fetch(
                """
                SELECT 
                    DATE(COALESCE(published_at, fetched_at)) as date,
                    COUNT(*) as total_articles,
                    COUNT(DISTINCT CASE WHEN EXISTS (
                        SELECT 1 FROM news_events ne WHERE ne.raw_news_id = raw_news.id
                    ) THEN raw_news.id END) as articles_with_events,
                    COUNT(DISTINCT CASE WHEN EXISTS (
                        SELECT 1 FROM news_events ne 
                        JOIN event_metrics em ON em.event_id = ne.id
                        WHERE ne.raw_news_id = raw_news.id
                    ) THEN raw_news.id END) as articles_with_metrics
                FROM raw_news
                GROUP BY DATE(COALESCE(published_at, fetched_at))
                ORDER BY date DESC
                LIMIT 10
                """
            )
            
            for row in articles_by_date:
                date = row['date']
                total = row['total_articles']
                with_events = row['articles_with_events']
                with_metrics = row['articles_with_metrics']
                
                events_pct = (with_events / total * 100) if total > 0 else 0
                metrics_pct = (with_metrics / total * 100) if total > 0 else 0
                
                print(f"{date}: {total} articles | Events: {with_events} ({events_pct:.0f}%) | Metrics: {with_metrics} ({metrics_pct:.0f}%)")
            
            # Check metrics creation timeline
            print("\n⏱️  Metrics Creation Timeline (last 24 hours):")
            print("─" * 100)
            
            metrics_timeline = await conn.fetch(
                """
                SELECT 
                    DATE_TRUNC('hour', created_at) as hour,
                    COUNT(*) as metrics_count
                FROM event_metrics
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                GROUP BY DATE_TRUNC('hour', created_at)
                ORDER BY hour DESC
                """
            )
            
            if metrics_timeline:
                for row in metrics_timeline:
                    hour = row['hour']
                    count = row['metrics_count']
                    print(f"{hour}: {count} metrics created")
            else:
                print("⚠️  No metrics created in last 24 hours")
            
            # Check events creation timeline
            print("\n⏱️  Events Creation Timeline (last 24 hours):")
            print("─" * 100)
            
            events_timeline = await conn.fetch(
                """
                SELECT 
                    DATE_TRUNC('hour', created_at) as hour,
                    COUNT(*) as events_count
                FROM news_events
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                GROUP BY DATE_TRUNC('hour', created_at)
                ORDER BY hour DESC
                """
            )
            
            if events_timeline:
                for row in events_timeline:
                    hour = row['hour']
                    count = row['events_count']
                    print(f"{hour}: {count} events created")
            else:
                print("⚠️  No events created in last 24 hours")
            
            # Check articles without metrics
            print("\n⚠️  Articles Without Metrics (last 2 days):")
            print("─" * 100)
            
            articles_without_metrics = await conn.fetch(
                """
                SELECT 
                    rn.id,
                    rn.title_original,
                    COALESCE(rn.published_at, rn.fetched_at) as date,
                    (SELECT COUNT(*) FROM news_events ne WHERE ne.raw_news_id = rn.id) as event_count
                FROM raw_news rn
                WHERE COALESCE(rn.published_at, rn.fetched_at) >= NOW() - INTERVAL '2 days'
                AND NOT EXISTS (
                    SELECT 1 FROM news_events ne2
                    JOIN event_metrics em ON em.event_id = ne2.id
                    WHERE ne2.raw_news_id = rn.id
                )
                ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC
                LIMIT 10
                """
            )
            
            if articles_without_metrics:
                print(f"Found {len(articles_without_metrics)} articles without metrics:")
                for row in articles_without_metrics:
                    print(f"  • ID: {row['id']} | Date: {row['date']} | Events: {row['event_count']}")
                    print(f"    Title: {row['title_original'][:80]}...")
            else:
                print("✅ All recent articles have metrics!")
            
            # Check has_numbers flag
            print("\n🔢 Articles with has_numbers=true (last 2 days):")
            print("─" * 100)
            
            has_numbers_count = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM raw_news
                WHERE has_numbers = true
                AND COALESCE(published_at, fetched_at) >= NOW() - INTERVAL '2 days'
                """
            )
            
            print(f"Articles with numbers: {has_numbers_count}")
            
            # Check processing status
            print("\n📊 Overall Processing Status:")
            print("─" * 100)
            
            total_articles = await conn.fetchval("SELECT COUNT(*) FROM raw_news")
            articles_with_events = await conn.fetchval(
                "SELECT COUNT(DISTINCT raw_news_id) FROM news_events"
            )
            articles_with_metrics = await conn.fetchval(
                """
                SELECT COUNT(DISTINCT ne.raw_news_id)
                FROM news_events ne
                JOIN event_metrics em ON em.event_id = ne.id
                """
            )
            
            print(f"Total articles: {total_articles}")
            print(f"Articles with events: {articles_with_events} ({articles_with_events/total_articles*100:.1f}%)")
            print(f"Articles with metrics: {articles_with_metrics} ({articles_with_metrics/total_articles*100:.1f}%)")
            
            # Recommendation
            print("\n💡 Recommendation:")
            print("─" * 100)
            
            if articles_without_metrics:
                print("⚠️  There are articles without metrics!")
                print("   Possible causes:")
                print("   1. Scheduler is not running")
                print("   2. Scheduler is running but has_numbers flag is false")
                print("   3. Articles don't have extractable numbers")
                print("\n   Solution:")
                print("   • Check if scheduler is running: python scripts/run_scheduler.py")
                print("   • Check has_numbers flag in articles")
                print("   • Run manual extraction: python scripts/run_forecast_generation.py")
            else:
                print("✅ All articles are being processed correctly!")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(check_scheduler_status())
