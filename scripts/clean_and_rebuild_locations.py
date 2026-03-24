#!/usr/bin/env python3
"""
Clean and Rebuild Locations Table
ينظف جدول المواقع ويعيد بناؤه من LOCATIONS_DATABASE فقط
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from app.core.config import settings
from app.services.geo.location_processor import LOCATIONS_DATABASE


async def main():
    """الدالة الرئيسية"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "تنظيف وإعادة بناء جدول المواقع".center(78) + "║")
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
            # 1. حذف جميع المواقع القديمة
            print("\n" + "=" * 80)
            print("1. حذف المواقع القديمة")
            print("=" * 80)
            
            # حذف الأحداث أولاً (لأنها مرتبطة بالمواقع)
            deleted_events = await conn.fetchval("DELETE FROM news_events")
            print(f"✓ تم حذف {deleted_events} حدث")
            
            # حذف المواقع
            deleted_locations = await conn.fetchval("DELETE FROM locations")
            print(f"✓ تم حذف {deleted_locations} موقع")
            
            # 2. إدراج المواقع الجديدة من LOCATIONS_DATABASE
            print("\n" + "=" * 80)
            print("2. إدراج المواقع الجديدة من LOCATIONS_DATABASE")
            print("=" * 80)
            
            inserted_count = 0
            
            for location_name, loc_data in LOCATIONS_DATABASE.items():
                try:
                    await conn.execute(
                        """
                        INSERT INTO locations (name, country_code, latitude, longitude, region_level, osm_id, osm_type)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        """,
                        location_name,
                        loc_data['country_code'],
                        loc_data['lat'],
                        loc_data['lng'],
                        loc_data['type'],
                        hash(location_name) % 2147483647,
                        'hardcoded'
                    )
                    inserted_count += 1
                    print(f"✓ {location_name} ({loc_data['country_code']})")
                except Exception as e:
                    print(f"✗ خطأ في إدراج {location_name}: {str(e)}")
            
            print(f"\n✓ تم إدراج {inserted_count} موقع")
            
            # 3. إحصائيات نهائية
            print("\n" + "=" * 80)
            print("3. الإحصائيات النهائية")
            print("=" * 80)
            
            total_locations = await conn.fetchval("SELECT COUNT(*) FROM locations")
            total_events = await conn.fetchval("SELECT COUNT(*) FROM news_events")
            
            # إحصائيات حسب الدول
            country_stats = await conn.fetch(
                """
                SELECT country_code, COUNT(*) as count
                FROM locations
                GROUP BY country_code
                ORDER BY count DESC
                """
            )
            
            print(f"\nإجمالي المواقع: {total_locations}")
            print(f"إجمالي الأحداث: {total_events}")
            
            print("\nتوزيع المواقع حسب الدول:")
            for row in country_stats:
                print(f"  {row['country_code']}: {row['count']} موقع")
            
            # 4. التحقق من عدم التكرار
            print("\n" + "=" * 80)
            print("4. التحقق من عدم التكرار")
            print("=" * 80)
            
            duplicates = await conn.fetch(
                """
                SELECT name, country_code, COUNT(*) as count
                FROM locations
                GROUP BY name, country_code
                HAVING COUNT(*) > 1
                """
            )
            
            if duplicates:
                print(f"✗ تم العثور على {len(duplicates)} موقع مكرر:")
                for dup in duplicates:
                    print(f"  - {dup['name']} ({dup['country_code']}): {dup['count']} نسخ")
            else:
                print("✓ لا توجد مواقع مكررة")
            
            print("\n" + "=" * 80)
            print("✓ تم إعادة بناء جدول المواقع بنجاح!")
            print("=" * 80 + "\n")
    
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
