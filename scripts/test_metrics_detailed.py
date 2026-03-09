#!/usr/bin/env python3
"""
Detailed Metrics Extraction Flow
يوضح كيف يشتغل الـ extraction خطوة بخطوة
"""

import sys
import os
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import db_manager
from app.services.extraction.metrics_extractor import extract_metrics


async def test_detailed_flow():
    """Show detailed metrics extraction flow"""
    
    print("=" * 80)
    print("📊 DETAILED METRICS EXTRACTION FLOW")
    print("=" * 80)
    
    # Connect to database
    print("\n🔗 Step 1: Connecting to database...")
    await db_manager.connect()
    pool = db_manager.get_pool()
    
    try:
        async with pool.acquire() as conn:
            # Step 1: Count statistics
            print("\n📈 Step 2: Database Statistics")
            print("─" * 80)
            
            total_articles = await conn.fetchval("SELECT COUNT(*) FROM raw_news")
            total_events = await conn.fetchval("SELECT COUNT(*) FROM news_events")
            total_metrics = await conn.fetchval("SELECT COUNT(*) FROM event_metrics")
            
            print(f"   • Total articles in DB: {total_articles}")
            print(f"   • Total events in DB: {total_events}")
            print(f"   • Total metrics in DB: {total_metrics}")
            
            # Step 2: Find events without metrics
            print("\n🔍 Step 3: Finding Events Without Metrics")
            print("─" * 80)
            
            events_without_metrics = await conn.fetch(
                """
                SELECT 
                    ne.id as event_id,
                    ne.place_name,
                    rn.id as article_id,
                    rn.title_original,
                    COALESCE(t.content, rn.content_original) as content,
                    rn.has_numbers
                FROM news_events ne
                JOIN raw_news rn ON rn.id = ne.raw_news_id
                LEFT JOIN translations t ON t.raw_news_id = rn.id
                WHERE rn.has_numbers = true
                AND (
                    (t.content IS NOT NULL AND LENGTH(t.content) > 50)
                    OR (rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 50)
                )
                AND NOT EXISTS (
                    SELECT 1 FROM event_metrics em WHERE em.event_id = ne.id
                )
                LIMIT 5
                """
            )
            
            print(f"   • Found {len(events_without_metrics)} events without metrics (showing first 5)")
            
            if not events_without_metrics:
                print("   ⚠️  No events found to process")
                return
            
            # Step 3: Process each event
            print("\n⚙️  Step 4: Processing Each Event")
            print("─" * 80)
            
            total_extracted = 0
            
            for idx, event in enumerate(events_without_metrics, 1):
                print(f"\n   Event {idx}/{len(events_without_metrics)}")
                print(f"   {'─' * 76}")
                
                event_id = event['event_id']
                article_id = event['article_id']
                place = event['place_name']
                title = event['title_original']
                content = event['content'] or ""
                
                print(f"   Event ID: {event_id}")
                print(f"   Article ID: {article_id}")
                print(f"   Place: {place}")
                print(f"   Title: {title[:60]}...")
                print(f"   Content length: {len(content)} chars")
                print(f"   Has numbers flag: {event['has_numbers']}")
                
                # Extract metrics
                print(f"\n   🔎 Extracting metrics from content...")
                metrics = extract_metrics(content)
                
                if metrics:
                    print(f"   ✅ Found {len(metrics)} metrics:")
                    for m in metrics:
                        print(f"      • {m['metric_type']}: {m['value']}")
                        print(f"        Snippet: {m['snippet'][:70]}...")
                    total_extracted += len(metrics)
                else:
                    print(f"   ⚠️  No metrics found")
            
            # Step 4: Summary
            print("\n" + "=" * 80)
            print("📊 SUMMARY")
            print("=" * 80)
            print(f"   • Events processed: {len(events_without_metrics)}")
            print(f"   • Metrics extracted: {total_extracted}")
            print(f"   • Average metrics per event: {total_extracted / len(events_without_metrics):.1f}")
            
            # Step 5: Show metric types
            print("\n📋 Metric Types Distribution (in database):")
            print("─" * 80)
            
            metric_types = await conn.fetch(
                """
                SELECT metric_type, COUNT(*) as count, AVG(value) as avg_value
                FROM event_metrics
                GROUP BY metric_type
                ORDER BY count DESC
                """
            )
            
            if metric_types:
                for mt in metric_types:
                    print(f"   • {mt['metric_type']}: {mt['count']} occurrences (avg: {mt['avg_value']:.0f})")
            else:
                print("   • No metrics in database yet")
            
            # Step 6: Show how scheduler would process
            print("\n🔄 How Scheduler Processes (every 15 minutes):")
            print("─" * 80)
            print(f"   1. Read batch_size=100 events without metrics")
            print(f"   2. For each event:")
            print(f"      - Extract metrics using regex patterns")
            print(f"      - Store in event_metrics table")
            print(f"   3. Repeat every 15 minutes")
            print(f"\n   Current unprocessed events: {len(events_without_metrics)}")
            print(f"   At batch_size=100, would take: {len(events_without_metrics) / 100:.1f} runs")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(test_detailed_flow())
