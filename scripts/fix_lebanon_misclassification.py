#!/usr/bin/env python3
"""
Fix Lebanon Misclassification
يصحح الأخبار اللي صُنّفت بـ "بنان" (تونس) بدل "بيروت" (لبنان)
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


async def find_misclassified_news(pool: asyncpg.Pool) -> list:
    """
    البحث عن الأخبار اللي صُنّفت بـ "بنان" (تونس) بدل "بيروت" (لبنان)
    """
    async with pool.acquire() as conn:
        # البحث عن أخبار مرتبطة بـ "بنان" في تونس
        rows = await conn.fetch(
            """
            SELECT DISTINCT
              ne.raw_news_id,
              rn.title_original,
              rn.content_original,
              l.name as location_name,
              l.country_code,
              l.latitude,
              l.longitude
            FROM news_events ne
            JOIN raw_news rn ON ne.raw_news_id = rn.id
            JOIN locations l ON ne.location_id = l.id
            WHERE l.name = 'بنان' AND l.country_code = 'TN'
            ORDER BY rn.published_at DESC NULLS LAST
            LIMIT 100
            """
        )
        return rows


async def find_correct_locations_in_news(text: str) -> list:
    """
    البحث عن المواقع الصحيحة في نص الخبر
    """
    locations = find_locations_in_text(text)
    return locations


async def get_location_id(conn: asyncpg.Connection, location_name: str, country_code: str) -> int:
    """الحصول على ID الموقع من قاعدة البيانات"""
    row = await conn.fetchrow(
        "SELECT id FROM locations WHERE name = $1 AND country_code = $2 LIMIT 1",
        location_name,
        country_code
    )
    if row:
        return int(row["id"])
    
    # إذا لم يوجد، أنشئه
    loc_data = LOCATIONS_DATABASE.get(location_name)
    if not loc_data:
        return None
    
    row = await conn.fetchrow(
        """
        INSERT INTO locations (name, country_code, latitude, longitude, region_level, osm_id, osm_type)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (name, country_code)
        DO UPDATE SET
          latitude = EXCLUDED.latitude,
          longitude = EXCLUDED.longitude
        RETURNING id
        """,
        location_name,
        loc_data['country_code'],
        loc_data['lat'],
        loc_data['lng'],
        loc_data['type'],
        hash(location_name) % 2147483647,
        'hardcoded'
    )
    return int(row["id"])


async def fix_misclassified_news(pool: asyncpg.Pool) -> dict:
    """
    تصحيح الأخبار المصنفة بشكل خاطئ
    """
    print("=" * 80)
    print("البحث عن الأخبار المصنفة بشكل خاطئ (بنان - تونس)")
    print("=" * 80)
    
    # البحث عن الأخبار المصنفة بشكل خاطئ
    misclassified = await find_misclassified_news(pool)
    
    if not misclassified:
        print("\n✓ لم يتم العثور على أخبار مصنفة بشكل خاطئ")
        return {
            "found": 0,
            "fixed": 0,
            "errors": 0
        }
    
    print(f"\n✗ تم العثور على {len(misclassified)} خبر مصنف بشكل خاطئ\n")
    
    fixed_count = 0
    error_count = 0
    
    async with pool.acquire() as conn:
        for i, row in enumerate(misclassified, 1):
            raw_news_id = int(row["raw_news_id"])
            title = row["title_original"][:50] + "..." if row["title_original"] else "بدون عنوان"
            
            print(f"{i}. معالجة الخبر #{raw_news_id}")
            print(f"   العنوان: {title}")
            
            # دمج العنوان والمحتوى
            text = (row["title_original"] or "") + "\n" + (row["content_original"] or "")
            
            # البحث عن المواقع الصحيحة
            correct_locations = await find_correct_locations_in_news(text)
            
            if not correct_locations:
                print(f"   ⚠ لم يتم العثور على مواقع صحيحة")
                error_count += 1
                continue
            
            print(f"   المواقع المكتشفة: {[name for name, _ in correct_locations]}")
            
            try:
                # حذف الربط الخاطئ (بنان - تونس)
                await conn.execute(
                    """
                    DELETE FROM news_events
                    WHERE raw_news_id = $1
                    AND location_id IN (
                        SELECT id FROM locations
                        WHERE name = 'بنان' AND country_code = 'TN'
                    )
                    """,
                    raw_news_id
                )
                
                # إضافة الروابط الصحيحة
                for location_name, loc_data in correct_locations:
                    location_id = await get_location_id(conn, location_name, loc_data['country_code'])
                    
                    if not location_id:
                        print(f"   ⚠ لم يتم العثور على ID للموقع: {location_name}")
                        continue
                    
                    # إضافة الربط الجديد
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
                    print(f"   ✓ تم إضافة: {location_name} ({loc_data['country_code']})")
                
                fixed_count += 1
                print(f"   ✓ تم تصحيح الخبر\n")
                
            except Exception as e:
                print(f"   ✗ خطأ: {str(e)}\n")
                error_count += 1
                continue
    
    print("=" * 80)
    print("النتائج")
    print("=" * 80)
    print(f"الأخبار المكتشفة: {len(misclassified)}")
    print(f"الأخبار المصححة: {fixed_count}")
    print(f"الأخطاء: {error_count}")
    print("=" * 80)
    
    return {
        "found": len(misclassified),
        "fixed": fixed_count,
        "errors": error_count
    }


async def verify_fix(pool: asyncpg.Pool) -> dict:
    """
    التحقق من أن التصحيح تم بشكل صحيح
    """
    print("\n" + "=" * 80)
    print("التحقق من التصحيح")
    print("=" * 80)
    
    async with pool.acquire() as conn:
        # البحث عن أي أخبار متبقية مصنفة بـ "بنان" - تونس
        remaining = await conn.fetchval(
            """
            SELECT COUNT(DISTINCT ne.raw_news_id)
            FROM news_events ne
            JOIN locations l ON ne.location_id = l.id
            WHERE l.name = 'بنان' AND l.country_code = 'TN'
            """
        )
        
        # البحث عن أخبار مصنفة بـ "بيروت" - لبنان
        beirut_count = await conn.fetchval(
            """
            SELECT COUNT(DISTINCT ne.raw_news_id)
            FROM news_events ne
            JOIN locations l ON ne.location_id = l.id
            WHERE l.name = 'بيروت' AND l.country_code = 'LB'
            """
        )
        
        print(f"\nأخبار متبقية مصنفة بـ 'بنان' (تونس): {remaining}")
        print(f"أخبار مصنفة بـ 'بيروت' (لبنان): {beirut_count}")
        
        if remaining == 0:
            print("\n✓ تم التصحيح بنجاح! لا توجد أخبار متبقية مصنفة بشكل خاطئ")
        else:
            print(f"\n⚠ لا تزال هناك {remaining} أخبار مصنفة بشكل خاطئ")
        
        print("=" * 80)
        
        return {
            "remaining_misclassified": remaining,
            "beirut_classified": beirut_count
        }


async def main():
    """الدالة الرئيسية"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "تصحيح تصنيف الأخبار - بنان (تونس) → بيروت (لبنان)".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # الاتصال بقاعدة البيانات
    try:
        pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=1, max_size=5)
    except Exception as e:
        print(f"\n✗ خطأ في الاتصال بقاعدة البيانات: {str(e)}")
        return
    
    try:
        # تصحيح الأخبار المصنفة بشكل خاطئ
        fix_result = await fix_misclassified_news(pool)
        
        # التحقق من التصحيح
        verify_result = await verify_fix(pool)
        
        # الملخص النهائي
        print("\n" + "=" * 80)
        print("الملخص النهائي")
        print("=" * 80)
        print(f"✓ الأخبار المصححة: {fix_result['fixed']}")
        print(f"✓ الأخبار المصنفة بـ 'بيروت' الآن: {verify_result['beirut_classified']}")
        print(f"✓ الأخبار المتبقية المصنفة بشكل خاطئ: {verify_result['remaining_misclassified']}")
        print("=" * 80 + "\n")
        
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
