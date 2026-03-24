#!/usr/bin/env python3
"""
Complete Pipeline Test
اختبار شامل للنظام كاملاً:
1. إدراج أخبار تجريبية
2. تشغيل معالجة المواقع
3. التحقق من الشروط (استثناء المصادر 17 و 18)
4. التحقق من استخراج المقاييس
"""

import asyncio
import asyncpg
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.geo.location_processor import process_locations
from app.services.extraction.metrics_processor import process_metrics


async def insert_test_data(pool):
    """Insert test news articles"""
    print("\n" + "="*80)
    print("STEP 1: INSERTING TEST DATA")
    print("="*80 + "\n")
    
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
        
        print("Inserting test articles:\n")
        
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
                    status = "✓" if article['should_create_events'] else "❌"
                    print(f"{i}. {status} Source {article['source_id']}: {article['title'][:50]}... (new)")
                else:
                    status = "✓" if article['should_create_events'] else "❌"
                    print(f"{i}. {status} Source {article['source_id']}: {article['title'][:50]}... (already exists)")
            except Exception as e:
                status = "✓" if article['should_create_events'] else "❌"
                print(f"{i}. {status} Source {article['source_id']}: {article['title'][:50]}... (skipped: {str(e)})")
        
        print(f"\n✅ Inserted/verified {len(test_articles)} test articles\n")


async def run_location_extraction(pool):
    """Run location extraction"""
    print("\n" + "="*80)
    print("STEP 2: RUNNING LOCATION EXTRACTION")
    print("="*80 + "\n")
    
    result = await process_locations(pool, batch_size=50)
    
    print(f"\n✅ Location extraction completed:")
    print(f"   • Articles processed: {result['processed_news']}")
    print(f"   • Locations detected: {result['places_detected']}")
    print(f"   • Events created: {result['events_created']}\n")
    
    return result


async def run_metrics_extraction(pool):
    """Run metrics extraction"""
    print("\n" + "="*80)
    print("STEP 3: RUNNING METRICS EXTRACTION")
    print("="*80 + "\n")
    
    result = await process_metrics(pool, batch_size=100)
    
    print(f"\n✅ Metrics extraction completed:")
    print(f"   • Events processed: {result['processed_events']}")
    print(f"   • Metrics extracted: {result['metrics_created']}\n")
    
    return result


async def verify_conditions(pool):
    """Verify all conditions"""
    print("\n" + "="*80)
    print("STEP 4: VERIFICATION")
    print("="*80 + "\n")
    
    async with pool.acquire() as conn:
        # Check 1: Events from sources 17 & 18 should be 0
        print("1️⃣  Checking source exclusion (17 & 18):")
        excluded_events = await conn.fetchval(
            """
            SELECT COUNT(*) FROM news_events ne
            JOIN raw_news rn ON ne.raw_news_id = rn.id
            WHERE rn.source_id IN (17, 18)
            """
        )
        
        if excluded_events == 0:
            print(f"   ✅ PASS: No events from sources 17 & 18 (found: {excluded_events})\n")
        else:
            print(f"   ❌ FAIL: Found {excluded_events} events from excluded sources!\n")
        
        # Check 2: Events from other sources should exist
        print("2️⃣  Checking events from allowed sources (7, 41):")
        allowed_events = await conn.fetchval(
            """
            SELECT COUNT(*) FROM news_events ne
            JOIN raw_news rn ON ne.raw_news_id = rn.id
            WHERE rn.source_id IN (7, 41)
            """
        )
        
        if allowed_events > 0:
            print(f"   ✅ PASS: Found {allowed_events} events from allowed sources\n")
        else:
            print(f"   ❌ FAIL: No events from allowed sources!\n")
        
        # Check 3: Events breakdown by source
        print("3️⃣  Events breakdown by source:")
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
                print(f"   ❌ Source {source_id}: {count} events (should be 0)")
            else:
                print(f"   ✓ Source {source_id}: {count} events")
        
        print()
        
        # Check 4: Locations by country
        print("4️⃣  Locations by country:")
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
                print(f"   • {row['country_code']}: {row['count']} locations")
        else:
            print("   (No locations found)")
        
        print()
        
        # Check 5: Metrics extraction
        print("5️⃣  Metrics extraction:")
        metrics_count = await conn.fetchval("SELECT COUNT(*) FROM event_metrics")
        
        if metrics_count > 0:
            print(f"   ✅ Found {metrics_count} metrics\n")
            
            metrics_by_type = await conn.fetch(
                """
                SELECT metric_type, COUNT(*) as count
                FROM event_metrics
                GROUP BY metric_type
                ORDER BY count DESC
                """
            )
            
            for row in metrics_by_type:
                print(f"   • {row['metric_type']}: {row['count']}")
        else:
            print(f"   ⚠️  No metrics found (this is OK if no events have numbers)\n")
        
        print()


async def main():
    """Main test function"""
    print("\n" + "="*80)
    print("COMPLETE PIPELINE TEST")
    print("="*80)
    
    # Connect to database
    try:
        pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=1,
            max_size=2,
            command_timeout=120
        )
    except Exception as e:
        print(f"\n❌ Failed to connect to database: {e}")
        return
    
    try:
        # Run all steps
        await insert_test_data(pool)
        await run_location_extraction(pool)
        await run_metrics_extraction(pool)
        await verify_conditions(pool)
        
        print("="*80)
        print("✅ COMPLETE PIPELINE TEST FINISHED")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
