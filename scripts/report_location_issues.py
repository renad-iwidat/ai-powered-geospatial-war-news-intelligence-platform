#!/usr/bin/env python3
"""
Report Location Issues
يعرض تقرير مفصل عن مشاكل التصنيف الجغرافي
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from app.core.config import settings


async def get_location_statistics(pool: asyncpg.Pool) -> dict:
    """الحصول على إحصائيات المواقع"""
    async with pool.acquire() as conn:
        # إجمالي الأخبار
        total_news = await conn.fetchval("SELECT COUNT(*) FROM raw_news")
        
        # الأخبار مع أحداث
        news_with_events = await conn.fetchval(
            "SELECT COUNT(DISTINCT raw_news_id) FROM news_events"
        )
        
        # إجمالي الأحداث
        total_events = await conn.fetchval("SELECT COUNT(*) FROM news_events")
        
        # المواقع المختلفة
        unique_locations = await conn.fetchval("SELECT COUNT(*) FROM locations")
        
        return {
            "total_news": total_news,
            "news_with_events": news_with_events,
            "total_events": total_events,
            "unique_locations": unique_locations
        }


async def find_duplicate_locations(pool: asyncpg.Pool) -> list:
    """البحث عن المواقع المكررة (نفس الاسم بدول مختلفة)"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT name, COUNT(*) as count, STRING_AGG(country_code, ', ') as countries
            FROM locations
            GROUP BY name
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            """
        )
        return rows


async def find_misclassified_locations(pool: asyncpg.Pool) -> dict:
    """البحث عن المواقع المصنفة بشكل خاطئ"""
    async with pool.acquire() as conn:
        # البحث عن "بنان" في تونس
        banan_tunisia = await conn.fetch(
            """
            SELECT 
              ne.raw_news_id,
              rn.title_original,
              rn.published_at,
              l.name,
              l.country_code
            FROM news_events ne
            JOIN raw_news rn ON ne.raw_news_id = rn.id
            JOIN locations l ON ne.location_id = l.id
            WHERE l.name = 'بنان' AND l.country_code = 'TN'
            ORDER BY rn.published_at DESC NULLS LAST
            LIMIT 20
            """
        )
        
        # البحث عن مواقع لبنانية
        lebanon_locations = await conn.fetch(
            """
            SELECT DISTINCT l.name, l.country_code, COUNT(ne.id) as event_count
            FROM locations l
            LEFT JOIN news_events ne ON l.id = ne.location_id
            WHERE l.country_code = 'LB'
            GROUP BY l.name, l.country_code
            ORDER BY event_count DESC
            """
        )
        
        return {
            "banan_tunisia": banan_tunisia,
            "lebanon_locations": lebanon_locations
        }


async def find_location_by_country(pool: asyncpg.Pool, country_code: str) -> list:
    """البحث عن جميع المواقع في دولة معينة"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT 
              l.name,
              l.country_code,
              COUNT(ne.id) as event_count,
              l.latitude,
              l.longitude
            FROM locations l
            LEFT JOIN news_events ne ON l.id = ne.location_id
            WHERE l.country_code = $1
            GROUP BY l.id, l.name, l.country_code, l.latitude, l.longitude
            ORDER BY event_count DESC
            """,
            country_code
        )
        return rows


async def main():
    """الدالة الرئيسية"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "تقرير مشاكل التصنيف الجغرافي".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # الاتصال بقاعدة البيانات
    try:
        pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=1, max_size=5)
    except Exception as e:
        print(f"\n✗ خطأ في الاتصال بقاعدة البيانات: {str(e)}")
        return
    
    try:
        # 1. الإحصائيات العامة
        print("\n" + "=" * 80)
        print("1. الإحصائيات العامة")
        print("=" * 80)
        
        stats = await get_location_statistics(pool)
        print(f"إجمالي الأخبار: {stats['total_news']}")
        print(f"الأخبار مع أحداث: {stats['news_with_events']}")
        print(f"إجمالي الأحداث: {stats['total_events']}")
        print(f"المواقع المختلفة: {stats['unique_locations']}")
        
        # 2. المواقع المكررة
        print("\n" + "=" * 80)
        print("2. المواقع المكررة (نفس الاسم بدول مختلفة)")
        print("=" * 80)
        
        duplicates = await find_duplicate_locations(pool)
        if duplicates:
            for dup in duplicates:
                print(f"\n{dup['name']}:")
                print(f"  عدد النسخ: {dup['count']}")
                print(f"  الدول: {dup['countries']}")
        else:
            print("✓ لا توجد مواقع مكررة")
        
        # 3. المواقع المصنفة بشكل خاطئ
        print("\n" + "=" * 80)
        print("3. المواقع المصنفة بشكل خاطئ")
        print("=" * 80)
        
        misclassified = await find_misclassified_locations(pool)
        
        # بنان - تونس
        print("\nأخبار مصنفة بـ 'بنان' (تونس):")
        if misclassified['banan_tunisia']:
            print(f"عدد الأخبار: {len(misclassified['banan_tunisia'])}")
            for i, row in enumerate(misclassified['banan_tunisia'][:5], 1):
                title = row['title_original'][:60] + "..." if row['title_original'] else "بدون عنوان"
                print(f"  {i}. {title}")
            if len(misclassified['banan_tunisia']) > 5:
                print(f"  ... و {len(misclassified['banan_tunisia']) - 5} أخبار أخرى")
        else:
            print("✓ لا توجد أخبار مصنفة بـ 'بنان' (تونس)")
        
        # المواقع اللبنانية
        print("\nالمواقع اللبنانية:")
        if misclassified['lebanon_locations']:
            for loc in misclassified['lebanon_locations']:
                print(f"  {loc['name']}: {loc['event_count']} حدث")
        else:
            print("✓ لا توجد مواقع لبنانية")
        
        # 4. المواقع حسب الدول
        print("\n" + "=" * 80)
        print("4. المواقع حسب الدول")
        print("=" * 80)
        
        countries = ['LB', 'SY', 'IQ', 'PS', 'JO', 'SA', 'AE', 'EG', 'TN']
        
        for country in countries:
            locations = await find_location_by_country(pool, country)
            if locations:
                country_name = {
                    'LB': 'لبنان',
                    'SY': 'سوريا',
                    'IQ': 'العراق',
                    'PS': 'فلسطين',
                    'JO': 'الأردن',
                    'SA': 'السعودية',
                    'AE': 'الإمارات',
                    'EG': 'مصر',
                    'TN': 'تونس'
                }.get(country, country)
                
                print(f"\n{country_name} ({country}):")
                for loc in locations:
                    print(f"  {loc['name']}: {loc['event_count']} حدث")
        
        # 5. التوصيات
        print("\n" + "=" * 80)
        print("5. التوصيات")
        print("=" * 80)
        
        if misclassified['banan_tunisia']:
            print(f"\n⚠ تم العثور على {len(misclassified['banan_tunisia'])} خبر مصنف بشكل خاطئ")
            print("التوصية: قم بتشغيل:")
            print("  python scripts/fix_lebanon_misclassification.py")
        else:
            print("\n✓ لا توجد مشاكل في التصنيف الجغرافي")
        
        print("\n" + "=" * 80 + "\n")
        
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
