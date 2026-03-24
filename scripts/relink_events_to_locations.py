#!/usr/bin/env python3
"""
Relink Events to Locations
يعيد ربط الأحداث بالمواقع الصحيحة من LOCATIONS_DATABASE
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from app.core.config import settings
from app.services.geo.location_processor import find_locations_in_text, LOCATIONS_DATABASE


async def get_ar_language_id(conn: asyncpg.Connection) -> int:
    """الحصول على ID اللغة العربية"""
    row = await conn.fetchrow("SELECT id FROM languages WHERE code='ar' LIMIT 1;")
    if not row:
        raise RuntimeError("Arabic language not found")
    return int(row["id"])


async def main():
    """الدالة الرئيسية"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "إعادة ربط الأحداث بالمواقع الصحيحة".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # الاتصال بقاعدة البيانات
    try:
        pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=1, max_size=5)
    except Exception as e:
        print(f"\n✗ خطأ في الاتصال بقاعدة البيانات: {str(e)}")
        return
    
    try:
        async with pool.acquire() as conn:
            # 1. حذف الأحداث القديمة
            print("\n" + "=" * 80)
            print("1. حذف الأحداث القديمة")
            print("=" * 80)
            
            deleted_events = await conn.fetchval("DELETE FROM news_events")
            print(f"✓ تم حذف {deleted_events} حدث")
            
            # 2. الحصول على الأخبار العربية
            print("\n" + "=" * 80)
            print("2. قراءة الأخبار العربية")
            print("=" * 80)
            
            ar_id = await get_ar_language_id(conn)
            
            news_rows = await conn.fetch(
                """
                SELECT
                  rn.id AS raw_news_id,
                  COALESCE(t.title, rn.title_original) AS title_ar,
                  COALESCE(t.content, rn.content_original) AS content_ar
                FROM raw_news rn
                LEFT JOIN translations t
                  ON t.raw_news_id = rn.id AND t.language_id = $1
                WHERE
                  (t.id IS NOT NULL OR rn.language_id = $1)
                ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC NULLS LAST
                LIMIT 1000
                """,
                ar_id
            )
            
            print(f"✓ تم قراءة {len(news_rows)} خبر")
            
            # 3. معالجة كل خبر
            print("\n" + "=" * 80)
            print("3. معالجة الأخبار واستخراج المواقع")
            print("=" * 80)
            
            processed = 0
            events_created = 0
            
            for i, news in enumerate(news_rows, 1):
                raw_news_id = news['raw_news_id']
                text = (news['title_ar'] or "") + "\n" + (news['content_ar'] or "")
                
                # استخراج المواقع
                locations = find_locations_in_text(text)
                
                if locations:
                    for location_name, loc_data in locations:
                        try:
                            # البحث عن الموقع في قاعدة البيانات
                            location = await conn.fetchrow(
                                "SELECT id FROM locations WHERE name = $1 AND country_code = $2",
                                location_name,
                                loc_data['country_code']
                            )
                            
                            if location:
                                location_id = location['id']
                                
                                # إنشاء الحدث
                                await conn.execute(
                                    """
                                    INSERT INTO news_events (raw_news_id, location_id, place_name, event_type)
                                    VALUES ($1, $2, $3, $4)
                                    ON CONFLICT (raw_news_id, location_id) DO NOTHING
                                    """,
                                    raw_news_id,
                                    location_id,
                                    location_name,
                                    "location_mention"
                                )
                                events_created += 1
                        except Exception as e:
                            print(f"✗ خطأ في معالجة {location_name}: {str(e)}")
                
                processed += 1
                
                if i % 100 == 0:
                    print(f"  معالجة {i}/{len(news_rows)} خبر...")
            
            print(f"\n✓ تم معالجة {processed} خبر")
            print(f"✓ تم إنشاء {events_created} حدث")
            
            # 4. الإحصائيات النهائية
            print("\n" + "=" * 80)
            print("4. الإحصائيات النهائية")
            print("=" * 80)
            
            total_news = await conn.fetchval("SELECT COUNT(*) FROM raw_news")
            news_with_events = await conn.fetchval(
                "SELECT COUNT(DISTINCT raw_news_id) FROM news_events"
            )
            total_events = await conn.fetchval("SELECT COUNT(*) FROM news_events")
            
            print(f"\nإجمالي الأخبار: {total_news}")
            print(f"الأخبار مع أحداث: {news_with_events}")
            print(f"إجمالي الأحداث: {total_events}")
            print(f"نسبة المعالجة: {(news_with_events/total_news*100):.1f}%")
            
            # إحصائيات حسب الدول
            country_stats = await conn.fetch(
                """
                SELECT 
                  l.country_code,
                  COUNT(DISTINCT ne.raw_news_id) as news_count,
                  COUNT(ne.id) as event_count
                FROM locations l
                LEFT JOIN news_events ne ON l.id = ne.location_id
                GROUP BY l.country_code
                ORDER BY event_count DESC
                """
            )
            
            print("\nتوزيع الأحداث حسب الدول:")
            for row in country_stats:
                if row['event_count'] > 0:
                    print(f"  {row['country_code']}: {row['event_count']} حدث ({row['news_count']} خبر)")
            
            print("\n" + "=" * 80)
            print("✓ تم إعادة ربط الأحداث بنجاح!")
            print("=" * 80 + "\n")
    
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
