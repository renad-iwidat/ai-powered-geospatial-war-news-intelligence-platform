#!/usr/bin/env python3
"""
Quick Scheduler Test
اختبار سريع للـ scheduler بدون الانتظار 15 دقيقة
يشغل معالجة البيانات مباشرة
"""

import sys
import os
import logging
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import setup_logging
from app.core.config import settings
from app.services.geo.location_processor import process_locations
from app.services.extraction.metrics_processor import process_metrics
import asyncpg

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


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
        return None
    
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
                },
                {
                    'source_id': 41,
                    'title': 'تطورات جديدة في دمشق',
                    'content': 'عقدت قيادات سياسية سورية اجتماعات مهمة في دمشق اليوم. حضر الاجتماع ممثلون من عدة دول عربية وأجنبية. ناقشوا الأوضاع الأمنية والاقتصادية في سوريا والمنطقة. أطلقت 20 صاروخاً في الهجمات.',
                    'hours_ago': 1,
                    'url': 'https://x.com/BBCArabic/status/2',
                },
                {
                    'source_id': 7,
                    'title': 'أنباء عن تطورات عسكرية في غزة',
                    'content': 'أفادت مصادر محلية عن تطورات عسكرية جديدة في قطاع غزة. قالت المصادر إن هناك تحركات عسكرية متزايدة في المنطقة. وأشارت إلى أن الوضع الإنساني يزداد سوءاً. أصيب 100 شخص في الاشتباكات.',
                    'hours_ago': 0.5,
                    'url': 'https://example.com/news/7',
                },
                {
                    'source_id': 17,
                    'title': 'أخبار من بيروت والعراق',
                    'content': 'أخبار من بيروت والعراق وفلسطين. هذا الخبر من مصدر 17 الذي يجب استثناؤه. لا يجب أن ينشئ events حتى لو كان يحتوي على أسماء مواقع.',
                    'hours_ago': 0.33,
                    'url': 'https://example.com/news/17',
                },
                {
                    'source_id': 18,
                    'title': 'أخبار من إيران والسعودية',
                    'content': 'أخبار من إيران والسعودية والإمارات. هذا الخبر من مصدر 18 الذي يجب استثناؤه. لا يجب أن ينشئ events حتى لو كان يحتوي على أسماء مواقع.',
                    'hours_ago': 0.25,
                    'url': 'https://example.com/news/18',
                },
                {
                    'source_id': 41,
                    'title': 'تطورات في القدس والضفة الغربية',
                    'content': 'شهدت القدس والضفة الغربية تطورات جديدة اليوم. أفادت مصادر محلية عن اشتباكات في عدة مناطق. وقالت إن الوضع الأمني متوتر جداً. دمرت 15 مبنى في الهجمات.',
                    'hours_ago': 0.17,
                    'url': 'https://x.com/BBCArabic/status/3',
                },
                {
                    'source_id': 41,
                    'title': 'بغداد تشهد احتجاجات واسعة',
                    'content': 'شهدت العاصمة العراقية بغداد احتجاجات واسعة اليوم. خرج آلاف المتظاهرين إلى الشوارع. طالبوا بتحسين الخدمات والقضاء على الفساد. أغلقت السلطات عدة طرق رئيسية في بغداد.',
                    'hours_ago': 0.08,
                    'url': 'https://x.com/BBCArabic/status/4',
                },
            ]
            
            logger.info("Inserting test articles:\n")
            
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
            
    except Exception as e:
        logger.error(f"❌ Error inserting test data: {e}", exc_info=True)
        return None
    
    finally:
        await pool.close()
    
    return pool


async def run_location_extraction(pool):
    """Run location extraction"""
    logger.info("\n" + "="*80)
    logger.info("STEP 2: RUNNING LOCATION EXTRACTION")
    logger.info("="*80 + "\n")
    
    result = await process_locations(pool, batch_size=50)
    
    logger.info(f"\n✅ Location extraction completed:")
    logger.info(f"   • Articles processed: {result['processed_news']}")
    logger.info(f"   • Locations detected: {result['places_detected']}")
    logger.info(f"   • Events created: {result['events_created']}\n")
    
    return result


async def run_metrics_extraction(pool):
    """Run metrics extraction"""
    logger.info("\n" + "="*80)
    logger.info("STEP 3: RUNNING METRICS EXTRACTION")
    logger.info("="*80 + "\n")
    
    result = await process_metrics(pool, batch_size=100)
    
    logger.info(f"\n✅ Metrics extraction completed:")
    logger.info(f"   • Events processed: {result['processed_events']}")
    logger.info(f"   • Metrics extracted: {result['metrics_created']}\n")
    
    return result


async def verify_results(pool):
    """Verify all results"""
    logger.info("\n" + "="*80)
    logger.info("STEP 4: VERIFICATION")
    logger.info("="*80 + "\n")
    
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
        
        logger.info("")
        
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
        
        logger.info("")
        
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
            logger.info(f"   ⚠️  No metrics found\n")
        
        logger.info("")


async def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("🚀 GeoNews AI - Quick Scheduler Test")
    logger.info("=" * 80)
    logger.info("")
    
    # Connect to database
    try:
        pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=1,
            max_size=2,
            command_timeout=120
        )
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        sys.exit(1)
    
    try:
        # Step 1: Insert test data
        await insert_test_data()
        
        # Step 2: Run location extraction
        await run_location_extraction(pool)
        
        # Step 3: Run metrics extraction
        await run_metrics_extraction(pool)
        
        # Step 4: Verify results
        await verify_results(pool)
        
        logger.info("=" * 80)
        logger.info("✅ QUICK SCHEDULER TEST COMPLETED")
        logger.info("=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
