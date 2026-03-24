#!/usr/bin/env python3
"""
Local Scheduler Runner with Test Data
يشغل الـ scheduler محلياً ويختبر الأخبار التجريبية
"""

import sys
import os
import logging
import asyncio
import signal
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import setup_logging
from app.core.config import settings
from app.services.scheduler import SchedulerManager
import asyncpg

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler_manager = None


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    global scheduler_manager
    logger.info("\n📛 Received shutdown signal, stopping scheduler...")
    if scheduler_manager:
        scheduler_manager.stop()
    logger.info("✅ Scheduler stopped")
    sys.exit(0)


async def insert_test_data():
    """Insert test news articles"""
    logger.info("\n" + "="*80)
    logger.info("STEP 1: INSERTING TEST DATA")
    logger.info("="*80 + "\n")
    
    try:
        pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=1,
            max_size=2,
            command_timeout=120
        )
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        return False
    
    try:
        async with pool.acquire() as conn:
            # Ensure Arabic language exists
            await conn.execute(
                "INSERT INTO languages (code, name) VALUES ('ar', 'Arabic') ON CONFLICT (code) DO NOTHING"
            )
            
            ar_id = await conn.fetchval("SELECT id FROM languages WHERE code='ar'")
            
            test_articles = [
                {
                    'source_id': 41,
                    'title': 'وزير الدفاع الإسرائيلي: نتوغل في الأراضي اللبنانية',
                    'content': 'وزير الدفاع الإسرائيلي أعلن اليوم عن عملية عسكرية جديدة في الأراضي اللبنانية. قال الوزير إن الهدف هو السيطرة على خط دفاع متقدم في المنطقة الحدودية. شارك في العملية آلاف الجنود والمعدات العسكرية الثقيلة. قتل حوالي 50 جندياً في الاشتباكات.',
                    'hours_ago': 2,
                    'url': 'https://x.com/BBCArabic/status/1',
                    'should_create_events': True,
                },
                {
                    'source_id': 41,
                    'title': 'تطورات جديدة في دمشق',
                    'content': 'عقدت قيادات سياسية سورية اجتماعات مهمة في دمشق اليوم. حضر الاجتماع ممثلون من عدة دول عربية وأجنبية. ناقشوا الأوضاع الأمنية والاقتصادية في سوريا والمنطقة. أطلقت 20 صاروخاً في الهجمات.',
                    'hours_ago': 1,
                    'url': 'https://x.com/BBCArabic/status/2',
                    'should_create_events': True,
                },
                {
                    'source_id': 7,
                    'title': 'أنباء عن تطورات عسكرية في غزة',
                    'content': 'أفادت مصادر محلية عن تطورات عسكرية جديدة في قطاع غزة. قالت المصادر إن هناك تحركات عسكرية متزايدة في المنطقة. وأشارت إلى أن الوضع الإنساني يزداد سوءاً. أصيب 100 شخص في الاشتباكات.',
                    'hours_ago': 0.5,
                    'url': 'https://example.com/news/7',
                    'should_create_events': True,
                },
                {
                    'source_id': 17,
                    'title': 'أخبار من بيروت والعراق',
                    'content': 'أخبار من بيروت والعراق وفلسطين. هذا الخبر من مصدر 17 الذي يجب استثناؤه. لا يجب أن ينشئ events حتى لو كان يحتوي على أسماء مواقع.',
                    'hours_ago': 0.33,
                    'url': 'https://example.com/news/17',
                    'should_create_events': False,
                },
                {
                    'source_id': 18,
                    'title': 'أخبار من إيران والسعودية',
                    'content': 'أخبار من إيران والسعودية والإمارات. هذا الخبر من مصدر 18 الذي يجب استثناؤه. لا يجب أن ينشئ events حتى لو كان يحتوي على أسماء مواقع.',
                    'hours_ago': 0.25,
                    'url': 'https://example.com/news/18',
                    'should_create_events': False,
                },
                {
                    'source_id': 41,
                    'title': 'تطورات في القدس والضفة الغربية',
                    'content': 'شهدت القدس والضفة الغربية تطورات جديدة اليوم. أفادت مصادر محلية عن اشتباكات في عدة مناطق. وقالت إن الوضع الأمني متوتر جداً. دمرت 15 مبنى في الهجمات.',
                    'hours_ago': 0.17,
                    'url': 'https://x.com/BBCArabic/status/3',
                    'should_create_events': True,
                },
                {
                    'source_id': 41,
                    'title': 'بغداد تشهد احتجاجات واسعة',
                    'content': 'شهدت العاصمة العراقية بغداد احتجاجات واسعة اليوم. خرج آلاف المتظاهرين إلى الشوارع. طالبوا بتحسين الخدمات والقضاء على الفساد. أغلقت السلطات عدة طرق رئيسية في بغداد.',
                    'hours_ago': 0.08,
                    'url': 'https://x.com/BBCArabic/status/4',
                    'should_create_events': True,
                },
            ]
            
            logger.info("Inserting test articles:\n")
            
            from datetime import datetime, timedelta
            
            for i, article in enumerate(test_articles, 1):
                published_at = datetime.utcnow() - timedelta(hours=article['hours_ago'])
                
                try:
                    result = await conn.fetchrow(
                        """
                        INSERT INTO raw_news 
                        (source_id, title_original, content_original, language_id, published_at, fetched_at, url)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (url) DO NOTHING
                        RETURNING id
                        """,
                        article['source_id'],
                        article['title'],
                        article['content'],
                        ar_id,
                        published_at,
                        datetime.utcnow(),
                        article['url']
                    )
                    
                    if result:
                        news_id = result['id']
                        logger.info(f"{i}. Source {article['source_id']}: {article['title'][:50]}... (new)")
                    else:
                        logger.info(f"{i}. Source {article['source_id']}: {article['title'][:50]}... (already exists)")
                except Exception as e:
                    logger.warning(f"{i}. Source {article['source_id']}: {article['title'][:50]}... (skipped: {str(e)})")
            
            logger.info(f"\n✅ Inserted {len(test_articles)} test articles\n")
            
            # Show summary
            counts = await conn.fetch(
                """
                SELECT source_id, COUNT(*) as count 
                FROM raw_news 
                WHERE source_id IN (7, 17, 18, 41) 
                GROUP BY source_id 
                ORDER BY source_id
                """
            )
            
            logger.info("Summary by source:")
            for row in counts:
                source_id = row['source_id']
                count = row['count']
                if source_id in (17, 18):
                    logger.info(f"  ❌ Source {source_id}: {count} articles (should be excluded)")
                else:
                    logger.info(f"  ✓ Source {source_id}: {count} articles")
            
            logger.info("")
            
    except Exception as e:
        logger.error(f"❌ Error inserting test data: {e}", exc_info=True)
        return False
    
    finally:
        await pool.close()
    
    return True


async def verify_before_scheduler():
    """Verify test data before running scheduler"""
    logger.info("\n" + "="*80)
    logger.info("STEP 2: VERIFYING TEST DATA")
    logger.info("="*80 + "\n")
    
    try:
        pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=1,
            max_size=2,
            command_timeout=120
        )
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        return False
    
    try:
        async with pool.acquire() as conn:
            # Count articles
            total_articles = await conn.fetchval(
                "SELECT COUNT(*) FROM raw_news WHERE source_id IN (7, 17, 18, 41)"
            )
            
            logger.info(f"Total test articles: {total_articles}")
            
            # Count existing events
            existing_events = await conn.fetchval(
                "SELECT COUNT(*) FROM news_events"
            )
            
            logger.info(f"Existing events in database: {existing_events}")
            logger.info("")
            
            if total_articles == 0:
                logger.error("❌ No test articles found!")
                return False
            
            logger.info("✅ Test data verified\n")
            
    except Exception as e:
        logger.error(f"❌ Error verifying data: {e}", exc_info=True)
        return False
    
    finally:
        await pool.close()
    
    return True


async def verify_after_scheduler():
    """Verify results after scheduler runs"""
    logger.info("\n" + "="*80)
    logger.info("STEP 4: VERIFYING RESULTS")
    logger.info("="*80 + "\n")
    
    try:
        pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=1,
            max_size=2,
            command_timeout=120
        )
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        return False
    
    try:
        async with pool.acquire() as conn:
            # Check 1: Events from sources 17 & 18 should be 0
            logger.info("1️⃣  Checking source exclusion (17 & 18):")
            excluded_events = await conn.fetchval(
                """
                SELECT COUNT(*) FROM news_events ne
                JOIN raw_news rn ON ne.raw_news_id = rn.id
                WHERE rn.source_id IN (17, 18)
                """
            )
            
            if excluded_events == 0:
                logger.info(f"   ✅ PASS: No events from sources 17 & 18 (found: {excluded_events})\n")
            else:
                logger.info(f"   ❌ FAIL: Found {excluded_events} events from excluded sources!\n")
            
            # Check 2: Events from other sources should exist
            logger.info("2️⃣  Checking events from allowed sources (7, 41):")
            allowed_events = await conn.fetchval(
                """
                SELECT COUNT(*) FROM news_events ne
                JOIN raw_news rn ON ne.raw_news_id = rn.id
                WHERE rn.source_id IN (7, 41)
                """
            )
            
            if allowed_events > 0:
                logger.info(f"   ✅ PASS: Found {allowed_events} events from allowed sources\n")
            else:
                logger.info(f"   ❌ FAIL: No events from allowed sources!\n")
            
            # Check 3: Events breakdown by source
            logger.info("3️⃣  Events breakdown by source:")
            breakdown = await conn.fetch(
                """
                SELECT rn.source_id, COUNT(*) as count
                FROM news_events ne
                JOIN raw_news rn ON ne.raw_news_id = rn.id
                WHERE rn.source_id IN (7, 17, 18, 41)
                GROUP BY rn.source_id
                ORDER BY rn.source_id
                """
            )
            
            for row in breakdown:
                source_id = row['source_id']
                count = row['count']
                if source_id in (17, 18):
                    logger.info(f"   ❌ Source {source_id}: {count} events (should be 0)")
                else:
                    logger.info(f"   ✓ Source {source_id}: {count} events")
            
            logger.info()
            
            # Check 4: Locations by country
            logger.info("4️⃣  Locations by country:")
            locations = await conn.fetch(
                """
                SELECT l.country_code, COUNT(DISTINCT l.id) as count
                FROM news_events ne
                JOIN locations l ON ne.location_id = l.id
                GROUP BY l.country_code
                ORDER BY count DESC
                LIMIT 10
                """
            )
            
            if locations:
                for row in locations:
                    logger.info(f"   • {row['country_code']}: {row['count']} locations")
            else:
                logger.info("   (No locations found)")
            
            logger.info()
            
            # Check 5: Metrics extraction
            logger.info("5️⃣  Metrics extraction:")
            metrics_count = await conn.fetchval("SELECT COUNT(*) FROM event_metrics")
            
            if metrics_count > 0:
                logger.info(f"   ✅ Found {metrics_count} metrics\n")
                
                metrics_by_type = await conn.fetch(
                    """
                    SELECT metric_type, COUNT(*) as count
                    FROM event_metrics
                    GROUP BY metric_type
                    ORDER BY count DESC
                    """
                )
                
                for row in metrics_by_type:
                    logger.info(f"   • {row['metric_type']}: {row['count']}")
            else:
                logger.info(f"   ⚠️  No metrics found (this is OK if no events have numbers)\n")
            
            logger.info()
            
    except Exception as e:
        logger.error(f"❌ Error verifying results: {e}", exc_info=True)
        return False
    
    finally:
        await pool.close()
    
    return True


def main():
    """Main entry point"""
    global scheduler_manager
    
    logger.info("=" * 80)
    logger.info("🚀 GeoNews AI - Local Scheduler Test")
    logger.info("=" * 80)
    logger.info("")
    
    # Step 1: Insert test data
    try:
        if not asyncio.run(insert_test_data()):
            logger.error("❌ Failed to insert test data")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error in insert_test_data: {e}", exc_info=True)
        sys.exit(1)
    
    # Step 2: Verify test data
    try:
        if not asyncio.run(verify_before_scheduler()):
            logger.error("❌ Failed to verify test data")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error in verify_before_scheduler: {e}", exc_info=True)
        sys.exit(1)
    
    # Step 3: Run scheduler
    logger.info("=" * 80)
    logger.info("STEP 3: RUNNING SCHEDULER")
    logger.info("=" * 80)
    logger.info("")
    
    api_base_url = "http://localhost:7235"
    
    logger.info(f"API Base URL: {api_base_url}")
    logger.info("")
    
    try:
        scheduler_manager = SchedulerManager(api_base_url=api_base_url)
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        scheduler_manager.start()
        
        logger.info("")
        logger.info("✅ Scheduler is running.")
        logger.info("📅 Scheduled Jobs:")
        logger.info("   • Data Processing: Every 15 minutes")
        logger.info("   • AI Forecast: Every 10 hours")
        logger.info("")
        logger.info("⏳ Waiting for first data processing cycle (15 minutes)...")
        logger.info("   (You can press Ctrl+C to stop)")
        logger.info("")
        
        # Wait for first cycle (15 minutes) or user interrupt
        time.sleep(15 * 60)
        
        logger.info("\n✅ First cycle completed!")
        
        # Step 4: Verify results
        try:
            asyncio.run(verify_after_scheduler())
        except Exception as e:
            logger.error(f"❌ Error in verify_after_scheduler: {e}", exc_info=True)
        
        # Stop scheduler
        scheduler_manager.stop()
        
    except KeyboardInterrupt:
        logger.info("\n📛 Received interrupt signal")
        if scheduler_manager:
            scheduler_manager.stop()
        
        # Verify results anyway
        logger.info("\n⏳ Verifying results before exit...")
        try:
            asyncio.run(verify_after_scheduler())
        except Exception as e:
            logger.error(f"❌ Error in verify_after_scheduler: {e}", exc_info=True)
        
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"❌ Failed to run scheduler: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
