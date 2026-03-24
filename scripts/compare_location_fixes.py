#!/usr/bin/env python3
"""
Compare Location Fixes
يعرض مقارنة قبل وبعد التصحيح
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from app.core.config import settings


async def get_location_stats_by_country(pool: asyncpg.Pool) -> dict:
    """الحصول على إحصائيات المواقع حسب الدول"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
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
        
        result = {}
        for row in rows:
            result[row['country_code']] = {
                'news_count': row['news_count'] or 0,
                'event_count': row['event_count'] or 0
            }
        return result


async def get_specific_location_stats(pool: asyncpg.Pool, location_name: str, country_code: str) -> dict:
    """الحصول على إحصائيات موقع محدد"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT 
              l.id,
              l.name,
              l.country_code,
              COUNT(DISTINCT ne.raw_news_id) as news_count,
              COUNT(ne.id) as event_count
            FROM locations l
            LEFT JOIN news_events ne ON l.id = ne.location_id
            WHERE l.name = $1 AND l.country_code = $2
            GROUP BY l.id, l.name, l.country_code
            """,
            location_name,
            country_code
        )
        
        if row:
            return {
                'name': row['name'],
                'country_code': row['country_code'],
                'news_count': row['news_count'] or 0,
                'event_count': row['event_count'] or 0
            }
        return None


async def get_sample_news(pool: asyncpg.Pool, location_name: str, country_code: str, limit: int = 5) -> list:
    """الحصول على عينة من الأخبار المصنفة بموقع محدد"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT 
              rn.id,
              rn.title_original,
              rn.published_at,
              l.name,
              l.country_code
            FROM news_events ne
            JOIN raw_news rn ON ne.raw_news_id = rn.id
            JOIN locations l ON ne.location_id = l.id
            WHERE l.name = $1 AND l.country_code = $2
            ORDER BY rn.published_at DESC NULLS LAST
            LIMIT $3
            """,
            location_name,
            country_code,
            limit
        )
        return rows


async def main():
    """الدالة الرئيسية"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "مقارنة تصحيح المواقع".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # الاتصال بقاعدة البيانات
    try:
        pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=1, max_size=5)
    except Exception as e:
        print(f"\n✗ خطأ في الاتصال بقاعدة البيانات: {str(e)}")
        return
    
    try:
        # 1. الإحصائيات حسب الدول
        print("\n" + "=" * 80)
        print("1. الإحصائيات حسب الدول")
        print("=" * 80)
        
        country_stats = await get_location_stats_by_country(pool)
        
        country_names = {
            'LB': 'لبنان',
            'SY': 'سوريا',
            'IQ': 'العراق',
            'PS': 'فلسطين',
            'JO': 'الأردن',
            'SA': 'السعودية',
            'AE': 'الإمارات',
            'EG': 'مصر',
            'TN': 'تونس',
            'TR': 'تركيا',
            'IR': 'إيران',
            'US': 'أمريكا',
            'GB': 'بريطانيا',
            'FR': 'فرنسا',
            'RU': 'روسيا',
            'CN': 'الصين',
            'IN': 'الهند',
            'JP': 'اليابان'
        }
        
        print(f"\n{'الدولة':<20} {'الأخبار':<15} {'الأحداث':<15}")
        print("-" * 50)
        
        for country_code in sorted(country_stats.keys()):
            stats = country_stats[country_code]
            country_name = country_names.get(country_code, country_code)
            print(f"{country_name:<20} {stats['news_count']:<15} {stats['event_count']:<15}")
        
        # 2. مقارنة بنان وبيروت
        print("\n" + "=" * 80)
        print("2. مقارنة بنان (تونس) وبيروت (لبنان)")
        print("=" * 80)
        
        banan_tn = await get_specific_location_stats(pool, 'بنان', 'TN')
        beirut_lb = await get_specific_location_stats(pool, 'بيروت', 'LB')
        
        print("\nبنان (تونس):")
        if banan_tn:
            print(f"  الأخبار: {banan_tn['news_count']}")
            print(f"  الأحداث: {banan_tn['event_count']}")
        else:
            print("  ✓ لا توجد أخبار")
        
        print("\nبيروت (لبنان):")
        if beirut_lb:
            print(f"  الأخبار: {beirut_lb['news_count']}")
            print(f"  الأحداث: {beirut_lb['event_count']}")
        else:
            print("  ✓ لا توجد أخبار")
        
        # 3. عينة من الأخبار المصنفة بـ "بنان" (تونس)
        print("\n" + "=" * 80)
        print("3. عينة من الأخبار المصنفة بـ 'بنان' (تونس)")
        print("=" * 80)
        
        banan_news = await get_sample_news(pool, 'بنان', 'TN', 10)
        
        if banan_news:
            print(f"\nعدد الأخبار: {len(banan_news)}")
            for i, news in enumerate(banan_news, 1):
                title = news['title_original'][:70] + "..." if news['title_original'] else "بدون عنوان"
                date = news['published_at'].strftime("%Y-%m-%d") if news['published_at'] else "بدون تاريخ"
                print(f"\n{i}. {title}")
                print(f"   التاريخ: {date}")
                print(f"   الموقع: {news['name']} ({news['country_code']})")
        else:
            print("\n✓ لا توجد أخبار مصنفة بـ 'بنان' (تونس)")
        
        # 4. عينة من الأخبار المصنفة بـ "بيروت" (لبنان)
        print("\n" + "=" * 80)
        print("4. عينة من الأخبار المصنفة بـ 'بيروت' (لبنان)")
        print("=" * 80)
        
        beirut_news = await get_sample_news(pool, 'بيروت', 'LB', 10)
        
        if beirut_news:
            print(f"\nعدد الأخبار: {len(beirut_news)}")
            for i, news in enumerate(beirut_news, 1):
                title = news['title_original'][:70] + "..." if news['title_original'] else "بدون عنوان"
                date = news['published_at'].strftime("%Y-%m-%d") if news['published_at'] else "بدون تاريخ"
                print(f"\n{i}. {title}")
                print(f"   التاريخ: {date}")
                print(f"   الموقع: {news['name']} ({news['country_code']})")
        else:
            print("\n✓ لا توجد أخبار مصنفة بـ 'بيروت' (لبنان)")
        
        # 5. الملخص
        print("\n" + "=" * 80)
        print("5. الملخص")
        print("=" * 80)
        
        total_events = sum(stats['event_count'] for stats in country_stats.values())
        total_news = sum(stats['news_count'] for stats in country_stats.values())
        
        print(f"\nإجمالي الأخبار: {total_news}")
        print(f"إجمالي الأحداث: {total_events}")
        
        if banan_tn and banan_tn['event_count'] > 0:
            print(f"\n⚠ تحذير: لا تزال هناك {banan_tn['event_count']} أحداث مصنفة بـ 'بنان' (تونس)")
            print("التوصية: قم بتشغيل:")
            print("  python scripts/fix_lebanon_misclassification.py")
        else:
            print("\n✓ لا توجد أخبار مصنفة بشكل خاطئ")
        
        print("\n" + "=" * 80 + "\n")
        
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
