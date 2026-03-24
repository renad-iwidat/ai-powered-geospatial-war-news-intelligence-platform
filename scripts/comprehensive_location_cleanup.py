#!/usr/bin/env python3
"""
Comprehensive Location Cleanup
يحل جميع مشاكل التصنيف الجغرافي:
1. Text Noise (فاصلات، نقاط، إلخ)
2. Duplicate Locations (نفس المكان بأشكال مختلفة)
3. Misclassification (مواقع بدول غلط)
4. Preprocessing issues (حروف جر ملتصقة)
"""

import sys
import os
import asyncio
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from app.core.config import settings
from app.services.geo.location_processor import LOCATIONS_DATABASE


# ============================================================================
# Normalization Rules
# ============================================================================

# قائمة التصحيحات (Mapping من الأسماء الخاطئة إلى الصحيحة)
LOCATION_CORRECTIONS = {
    # Text Noise - إزالة الفاصلات والرموز
    'بيروت،': 'بيروت',
    'بيروت:': 'بيروت',
    'بيروت.': 'بيروت',
    'لبنان،': 'لبنان',
    'لبنان:': 'لبنان',
    'لبنان.': 'لبنان',
    'دمشق،': 'دمشق',
    'دمشق:': 'دمشق',
    'دمشق.': 'دمشق',
    'بغداد،': 'بغداد',
    'بغداد:': 'بغداد',
    'بغداد.': 'بغداد',
    
    # Preprocessing issues - حروف جر ملتصقة
    'وايران': 'إيران',
    'والعراق': 'العراق',
    'وسوريا': 'سوريا',
    'ولبنان': 'لبنان',
    'وفلسطين': 'فلسطين',
    'والأردن': 'الأردن',
    'والسعودية': 'السعودية',
    'والإمارات': 'الإمارات',
    'ومصر': 'مصر',
    'وتونس': 'تونس',
    'والعراق:': 'العراق',
    'والعراق،': 'العراق',
    'والعراق.': 'العراق',
    
    # Misclassification - مواقع بدول غلط
    'نيو مكسيكو': None,  # حذف - ليست في الشرق الأوسط
    'اميركا': 'أمريكا',
    'امريكا': 'أمريكا',
    'حر العرب': None,  # حذف - ليست موقع
    'غداد': 'بغداد',  # تصحيح
    'غداد،': 'بغداد',
    'غداد:': 'بغداد',
    'غداد.': 'بغداد',
    
    # Duplicate variations
    'ولبنان': 'لبنان',
    'ولبنان،': 'لبنان',
    'ولبنان:': 'لبنان',
    'ولبنان.': 'لبنان',
    'بنان': 'لبنان',  # الخطأ الأساسي
    'بنان،': 'لبنان',
    'بنان:': 'لبنان',
    'بنان.': 'لبنان',
    
    # فلسطين variations
    'غزه': 'غزة',
    'غزه،': 'غزة',
    'غزه:': 'غزة',
    'غزه.': 'غزة',
    'غزة،': 'غزة',
    'غزة:': 'غزة',
    'غزة.': 'غزة',
}

# مواقع يجب حذفها (ليست مواقع حقيقية أو خارج النطاق)
LOCATIONS_TO_DELETE = {
    'نيو مكسيكو',
    'حر العرب',
    'وايران',
    'والعراق',
    'وسوريا',
    'ولبنان',
    'وفلسطين',
    'والأردن',
    'والسعودية',
    'والإمارات',
    'ومصر',
    'وتونس',
}


# ============================================================================
# Helper Functions
# ============================================================================

async def normalize_location_names(pool: asyncpg.Pool) -> dict:
    """
    تطبيع أسماء المواقع:
    1. إزالة الرموز الإضافية
    2. توحيد الأسماء المكررة
    3. حذف المواقع غير الصحيحة
    """
    print("\n" + "=" * 80)
    print("1. تطبيع أسماء المواقع")
    print("=" * 80)
    
    stats = {
        'corrected': 0,
        'deleted': 0,
        'errors': 0
    }
    
    async with pool.acquire() as conn:
        # الحصول على جميع المواقع
        all_locations = await conn.fetch("SELECT id, name, country_code FROM locations")
        
        for location in all_locations:
            loc_id = location['id']
            old_name = location['name']
            country_code = location['country_code']
            
            # البحث عن تصحيح
            new_name = LOCATION_CORRECTIONS.get(old_name)
            
            if new_name is None and old_name in LOCATIONS_TO_DELETE:
                # حذف الموقع
                try:
                    # حذف الأحداث المرتبطة
                    await conn.execute(
                        "DELETE FROM news_events WHERE location_id = $1",
                        loc_id
                    )
                    # حذف الموقع
                    await conn.execute(
                        "DELETE FROM locations WHERE id = $1",
                        loc_id
                    )
                    print(f"✓ تم حذف: {old_name}")
                    stats['deleted'] += 1
                except Exception as e:
                    print(f"✗ خطأ في حذف {old_name}: {str(e)}")
                    stats['errors'] += 1
                continue
            
            if new_name and new_name != old_name:
                # تصحيح الاسم
                try:
                    # البحث عن الموقع الجديد
                    new_location = await conn.fetchrow(
                        "SELECT id FROM locations WHERE name = $1 AND country_code = $2",
                        new_name,
                        country_code
                    )
                    
                    if new_location:
                        new_loc_id = new_location['id']
                        
                        # نقل جميع الأحداث من الموقع القديم إلى الجديد
                        await conn.execute(
                            """
                            UPDATE news_events
                            SET location_id = $1
                            WHERE location_id = $2
                            """,
                            new_loc_id,
                            loc_id
                        )
                        
                        # حذف الموقع القديم
                        await conn.execute(
                            "DELETE FROM locations WHERE id = $1",
                            loc_id
                        )
                        
                        print(f"✓ تم تصحيح: {old_name} → {new_name}")
                        stats['corrected'] += 1
                    else:
                        # إنشاء الموقع الجديد إذا لم يكن موجوداً
                        loc_data = LOCATIONS_DATABASE.get(new_name)
                        if loc_data:
                            new_row = await conn.fetchrow(
                                """
                                INSERT INTO locations (name, country_code, latitude, longitude, region_level, osm_id, osm_type)
                                VALUES ($1, $2, $3, $4, $5, $6, $7)
                                ON CONFLICT (name, country_code)
                                DO UPDATE SET latitude = EXCLUDED.latitude
                                RETURNING id
                                """,
                                new_name,
                                loc_data['country_code'],
                                loc_data['lat'],
                                loc_data['lng'],
                                loc_data['type'],
                                hash(new_name) % 2147483647,
                                'hardcoded'
                            )
                            new_loc_id = new_row['id']
                            
                            # نقل الأحداث
                            await conn.execute(
                                """
                                UPDATE news_events
                                SET location_id = $1
                                WHERE location_id = $2
                                """,
                                new_loc_id,
                                loc_id
                            )
                            
                            # حذف الموقع القديم
                            await conn.execute(
                                "DELETE FROM locations WHERE id = $1",
                                loc_id
                            )
                            
                            print(f"✓ تم تصحيح وإنشاء: {old_name} → {new_name}")
                            stats['corrected'] += 1
                        else:
                            print(f"⚠ لم يتم العثور على {new_name} في قاعدة البيانات")
                            stats['errors'] += 1
                
                except Exception as e:
                    print(f"✗ خطأ في تصحيح {old_name}: {str(e)}")
                    stats['errors'] += 1
    
    return stats


async def remove_duplicate_locations(pool: asyncpg.Pool) -> dict:
    """
    إزالة المواقع المكررة (نفس الموقع بأكثر من ID)
    """
    print("\n" + "=" * 80)
    print("2. إزالة المواقع المكررة")
    print("=" * 80)
    
    stats = {
        'merged': 0,
        'errors': 0
    }
    
    async with pool.acquire() as conn:
        # البحث عن المواقع المكررة
        duplicates = await conn.fetch(
            """
            SELECT name, country_code, COUNT(*) as count, ARRAY_AGG(id) as ids
            FROM locations
            GROUP BY name, country_code
            HAVING COUNT(*) > 1
            """
        )
        
        for dup in duplicates:
            name = dup['name']
            country_code = dup['country_code']
            ids = dup['ids']
            
            try:
                # الاحتفاظ بأول ID وحذف الباقي
                keep_id = ids[0]
                delete_ids = ids[1:]
                
                for delete_id in delete_ids:
                    # نقل الأحداث
                    await conn.execute(
                        """
                        UPDATE news_events
                        SET location_id = $1
                        WHERE location_id = $2
                        """,
                        keep_id,
                        delete_id
                    )
                    
                    # حذف الموقع المكرر
                    await conn.execute(
                        "DELETE FROM locations WHERE id = $1",
                        delete_id
                    )
                
                print(f"✓ تم دمج: {name} ({country_code}) - {len(delete_ids)} نسخة محذوفة")
                stats['merged'] += 1
                
            except Exception as e:
                print(f"✗ خطأ في دمج {name}: {str(e)}")
                stats['errors'] += 1
    
    return stats


async def fix_country_mapping(pool: asyncpg.Pool) -> dict:
    """
    تصحيح تعيين الدول (مثل نيو مكسيكو بالإمارات)
    """
    print("\n" + "=" * 80)
    print("3. تصحيح تعيين الدول")
    print("=" * 80)
    
    stats = {
        'fixed': 0,
        'errors': 0
    }
    
    async with pool.acquire() as conn:
        # البحث عن مواقع بدول غير صحيحة
        wrong_mappings = await conn.fetch(
            """
            SELECT DISTINCT l.id, l.name, l.country_code
            FROM locations l
            WHERE l.name NOT IN (SELECT name FROM (
                SELECT name FROM (VALUES
                    ('بيروت'), ('دمشق'), ('بغداد'), ('طهران'), ('الرياض'), ('دبي'),
                    ('القاهرة'), ('تونس'), ('الجزائر'), ('طرابلس'), ('صنعاء'), ('مسقط'),
                    ('الكويت'), ('الدوحة'), ('المنامة'), ('القدس'), ('غزة'), ('إسطنبول'),
                    ('أنقرة'), ('باريس'), ('لندن'), ('نيويورك'), ('موسكو'), ('دلهي'),
                    ('بكين'), ('طوكيو'), ('لبنان'), ('سوريا'), ('فلسطين'), ('العراق'),
                    ('إيران'), ('السعودية'), ('الإمارات'), ('مصر'), ('الأردن'), ('تونس'),
                    ('المغرب'), ('الجزائر'), ('ليبيا'), ('اليمن'), ('عمان'), ('الكويت'),
                    ('قطر'), ('البحرين'), ('إسرائيل'), ('تركيا'), ('اليونان'), ('فرنسا'),
                    ('بريطانيا'), ('أمريكا'), ('روسيا'), ('الهند'), ('الصين'), ('اليابان'),
                    ('عمّان')
                ) AS t(name)
            ) AS valid_names)
            LIMIT 50
            """
        )
        
        for mapping in wrong_mappings:
            loc_id = mapping['id']
            name = mapping['name']
            country_code = mapping['country_code']
            
            # البحث عن الموقع الصحيح في LOCATIONS_DATABASE
            correct_data = LOCATIONS_DATABASE.get(name)
            
            if correct_data and correct_data['country_code'] != country_code:
                try:
                    # تحديث الموقع بالبيانات الصحيحة
                    await conn.execute(
                        """
                        UPDATE locations
                        SET country_code = $1, latitude = $2, longitude = $3
                        WHERE id = $4
                        """,
                        correct_data['country_code'],
                        correct_data['lat'],
                        correct_data['lng'],
                        loc_id
                    )
                    
                    print(f"✓ تم تصحيح: {name} من {country_code} إلى {correct_data['country_code']}")
                    stats['fixed'] += 1
                    
                except Exception as e:
                    print(f"✗ خطأ في تصحيح {name}: {str(e)}")
                    stats['errors'] += 1
    
    return stats


async def main():
    """الدالة الرئيسية"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "تنظيف شامل لنظام التصنيف الجغرافي".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # الاتصال بقاعدة البيانات
    try:
        pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=1, max_size=5)
    except Exception as e:
        print(f"\n✗ خطأ في الاتصال بقاعدة البيانات: {str(e)}")
        return
    
    try:
        # تطبيع أسماء المواقع
        norm_stats = await normalize_location_names(pool)
        
        # إزالة المواقع المكررة
        dup_stats = await remove_duplicate_locations(pool)
        
        # تصحيح تعيين الدول
        country_stats = await fix_country_mapping(pool)
        
        # الملخص النهائي
        print("\n" + "=" * 80)
        print("الملخص النهائي")
        print("=" * 80)
        print(f"\n✓ تطبيع الأسماء:")
        print(f"  - تم تصحيح: {norm_stats['corrected']}")
        print(f"  - تم حذف: {norm_stats['deleted']}")
        print(f"  - أخطاء: {norm_stats['errors']}")
        
        print(f"\n✓ إزالة المكررات:")
        print(f"  - تم دمج: {dup_stats['merged']}")
        print(f"  - أخطاء: {dup_stats['errors']}")
        
        print(f"\n✓ تصحيح تعيين الدول:")
        print(f"  - تم تصحيح: {country_stats['fixed']}")
        print(f"  - أخطاء: {country_stats['errors']}")
        
        total_fixed = norm_stats['corrected'] + dup_stats['merged'] + country_stats['fixed']
        print(f"\n✓ إجمالي التصحيحات: {total_fixed}")
        print("=" * 80 + "\n")
        
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
