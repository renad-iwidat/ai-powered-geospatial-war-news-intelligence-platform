#!/usr/bin/env python3
"""
Insert Test News Articles for Local Testing
يدرج أخبار تجريبية من مصادر مختلفة لاختبار الشروط
"""

import asyncio
import asyncpg
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


async def insert_test_news():
    """Insert test news articles"""
    
    print("\n" + "="*80)
    print("INSERTING TEST NEWS ARTICLES")
    print("="*80 + "\n")
    
    # Connect to database
    try:
        pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=1,
            max_size=2,
            command_timeout=120
        )
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return
    
    try:
        async with pool.acquire() as conn:
            # Ensure Arabic language exists
            print("1️⃣  Ensuring Arabic language exists...")
            await conn.execute(
                "INSERT INTO languages (code, name) VALUES ('ar', 'Arabic') ON CONFLICT (code) DO NOTHING"
            )
            
            ar_id = await conn.fetchval("SELECT id FROM languages WHERE code='ar'")
            print(f"   ✓ Arabic language ID: {ar_id}\n")
            
            # Test data
            test_articles = [
                {
                    'source_id': 41,
                    'title': 'وزير الدفاع الإسرائيلي: نتوغل في الأراضي اللبنانية للسيطرة على خط دفاع متقدم',
                    'content': 'شاهد معنا بي بي سي نيوز عربي على موقعنا وعلى قناتنا على يوتيوب. وزير الدفاع الإسرائيلي أعلن اليوم عن عملية عسكرية جديدة في الأراضي اللبنانية. قال الوزير إن الهدف هو السيطرة على خط دفاع متقدم في المنطقة الحدودية. شارك في العملية آلاف الجنود والمعدات العسكرية الثقيلة.',
                    'hours_ago': 2,
                    'url': 'https://x.com/BBCArabic/status/2036398263062925717',
                    'should_create_events': True,
                    'description': 'BBC Arabic - يجب أن ينشئ events'
                },
                {
                    'source_id': 41,
                    'title': 'تطورات جديدة في دمشق: اجتماعات سياسية مهمة',
                    'content': 'عقدت قيادات سياسية سورية اجتماعات مهمة في دمشق اليوم. حضر الاجتماع ممثلون من عدة دول عربية وأجنبية. ناقشوا الأوضاع الأمنية والاقتصادية في سوريا والمنطقة. أكدوا على أهمية الاستقرار والسلام.',
                    'hours_ago': 1,
                    'url': 'https://x.com/BBCArabic/status/2036398263062925718',
                    'should_create_events': True,
                    'description': 'BBC Arabic - يجب أن ينشئ events'
                },
                {
                    'source_id': 7,
                    'title': 'أنباء عن تطورات عسكرية في غزة',
                    'content': 'أفادت مصادر محلية عن تطورات عسكرية جديدة في قطاع غزة. قالت المصادر إن هناك تحركات عسكرية متزايدة في المنطقة. وأشارت إلى أن الوضع الإنساني يزداد سوءاً. طالبت المنظمات الدولية بتدخل فوري لإيقاف العنف.',
                    'hours_ago': 0.5,
                    'url': 'https://example.com/news/7',
                    'should_create_events': True,
                    'description': 'مصدر عادي (7) - يجب أن ينشئ events'
                },
                {
                    'source_id': 17,
                    'title': 'أخبار من بيروت والعراق',
                    'content': 'أخبار من بيروت والعراق وفلسطين. هذا الخبر من مصدر 17 الذي يجب استثناؤه. لا يجب أن ينشئ events حتى لو كان يحتوي على أسماء مواقع.',
                    'hours_ago': 0.33,
                    'url': 'https://example.com/news/17',
                    'should_create_events': False,
                    'description': '❌ مصدر 17 (مستثنى) - لا يجب أن ينشئ events'
                },
                {
                    'source_id': 18,
                    'title': 'أخبار من إيران والسعودية',
                    'content': 'أخبار من إيران والسعودية والإمارات. هذا الخبر من مصدر 18 الذي يجب استثناؤه. لا يجب أن ينشئ events حتى لو كان يحتوي على أسماء مواقع.',
                    'hours_ago': 0.25,
                    'url': 'https://example.com/news/18',
                    'should_create_events': False,
                    'description': '❌ مصدر 18 (مستثنى) - لا يجب أن ينشئ events'
                },
                {
                    'source_id': 41,
                    'title': 'تطورات في القدس والضفة الغربية',
                    'content': 'شهدت القدس والضفة الغربية تطورات جديدة اليوم. أفادت مصادر محلية عن اشتباكات في عدة مناطق. وقالت إن الوضع الأمني متوتر جداً. طالبت المنظمات الإنسانية بوقف فوري للعنف.',
                    'hours_ago': 0.17,
                    'url': 'https://x.com/BBCArabic/status/2036398263062925719',
                    'should_create_events': True,
                    'description': 'BBC Arabic - يجب أن ينشئ events'
                },
                {
                    'source_id': 41,
                    'title': 'بغداد تشهد احتجاجات واسعة',
                    'content': 'شهدت العاصمة العراقية بغداد احتجاجات واسعة اليوم. خرج آلاف المتظاهرين إلى الشوارع. طالبوا بتحسين الخدمات والقضاء على الفساد. أغلقت السلطات عدة طرق رئيسية في بغداد.',
                    'hours_ago': 0.08,
                    'url': 'https://x.com/BBCArabic/status/2036398263062925720',
                    'should_create_events': True,
                    'description': 'BBC Arabic - يجب أن ينشئ events'
                },
            ]
            
            # Insert articles
            print("2️⃣  Inserting test articles...\n")
            
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
                        print(f"   {i}. {status} {article['description']}")
                        print(f"      ID: {news_id}, Source: {article['source_id']}")
                        print(f"      Title: {article['title'][:60]}... (new)\n")
                    else:
                        status = "✓" if article['should_create_events'] else "❌"
                        print(f"   {i}. {status} {article['description']}")
                        print(f"      Source: {article['source_id']}")
                        print(f"      Title: {article['title'][:60]}... (already exists)\n")
                except Exception as e:
                    status = "✓" if article['should_create_events'] else "❌"
                    print(f"   {i}. {status} {article['description']}")
                    print(f"      Source: {article['source_id']}")
                    print(f"      Title: {article['title'][:60]}... (skipped: {str(e)})\n")
            
            # Verification queries
            print("\n" + "="*80)
            print("VERIFICATION")
            print("="*80 + "\n")
            
            # Count articles by source
            print("3️⃣  Articles by source:")
            counts = await conn.fetch(
                """
                SELECT source_id, COUNT(*) as count 
                FROM raw_news 
                WHERE source_id IN (7, 17, 18, 41) 
                GROUP BY source_id 
                ORDER BY source_id
                """
            )
            
            for row in counts:
                source_id = row['source_id']
                count = row['count']
                if source_id in (17, 18):
                    print(f"   ❌ Source {source_id}: {count} articles (should be excluded)")
                else:
                    print(f"   ✓ Source {source_id}: {count} articles")
            
            print("\n4️⃣  Next steps:")
            print("   1. Run the scheduler or location extraction endpoint")
            print("   2. Check that events are created ONLY from sources 7 and 41")
            print("   3. Verify NO events are created from sources 17 and 18")
            print("   4. Check the logging output for location extraction details\n")
            
            print("="*80)
            print("✅ TEST DATA INSERTED SUCCESSFULLY")
            print("="*80 + "\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(insert_test_news())
