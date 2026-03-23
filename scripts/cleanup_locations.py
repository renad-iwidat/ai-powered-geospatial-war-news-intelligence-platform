#!/usr/bin/env python3
"""
Script to cleanup incorrect locations in the database
يحذف المواقع الخاطئة ويصحح الإحداثيات
"""

import asyncio
import asyncpg
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings

# ============================================================================
# قائمة المواقع الخاطئة التي يجب حذفها
# ============================================================================
LOCATIONS_TO_DELETE = [
    # (name, country_code) - المواقع الخاطئة
    ('بنان', 'TN'),  # بنان من تونس (خطأ - يجب أن تكون لبنان)
    ('ندر عباس', 'IR'),  # اسم خاطئ
    ('يرث:', 'SY'),  # اسم خاطئ
    ('ميناب', 'IR'),  # اسم خاطئ
    ('ردفان', 'YE'),  # اسم خاطئ
    ('القنيطره', 'IQ'),  # اسم خاطئ
    ('امريكا اللاتينيه', 'EG'),  # موقع خاطئ
    ('سيدي بوسعيد،', 'TN'),  # اسم به علامات ترقيم
    ('موريتانيا:', 'MR'),  # اسم به علامات ترقيم
    ('المغرب:', 'MA'),  # اسم به علامات ترقيم
    ('ليبيا،', 'LY'),  # اسم به علامات ترقيم
    ('بولندا،', 'PL'),  # اسم به علامات ترقيم
    ('الشرق الاوسط،', 'IQ'),  # ليس مكان محدد
    ('اوسلو:', 'NO'),  # اسم به علامات ترقيم
    ('اوكرانيا', 'UA'),  # إحداثيات خاطئة
    ('اوروبا', 'UNKNOWN'),  # قارة وليس دولة
    ('اسيا', 'UNKNOWN'),  # قارة وليس دولة
    ('استراليا', 'UNKNOWN'),  # إحداثيات خاطئة
    ('البحر المتوسط', 'UNKNOWN'),  # بحر وليس مكان
]

# ============================================================================
# قائمة المواقع التي يجب تصحيح إحداثياتها
# ============================================================================
LOCATIONS_TO_FIX = {
    # (name, country_code): (new_lat, new_lng)
    ('دمشق', 'SY'): (33.5138, 36.2765),
    ('بغداد', 'IQ'): (33.3128, 44.3615),
    ('طهران', 'IR'): (35.6892, 51.3890),
    ('الرياض', 'SA'): (24.7136, 46.6753),
    ('دبي', 'AE'): (25.2048, 55.2708),
    ('القاهرة', 'EG'): (30.0444, 31.2357),
    ('بيروت', 'LB'): (33.8886, 35.4955),
    ('عمّان', 'JO'): (31.9539, 35.9106),  # تحسين الإحداثيات
    ('تونس', 'TN'): (36.8065, 10.1686),
    ('الجزائر', 'DZ'): (36.7538, 3.0588),
    ('طرابلس', 'LY'): (32.8872, 13.1913),
    ('مسقط', 'OM'): (23.6100, 58.5400),
    ('الكويت', 'KW'): (29.3759, 47.9774),
    ('الدوحة', 'QA'): (25.2854, 51.5310),
    ('المنامة', 'BH'): (26.2167, 50.5833),
    ('القدس', 'PS'): (31.7683, 35.2137),
    ('غزة', 'PS'): (31.5017, 34.4668),  # تصحيح الإحداثيات (كانت قرب الضفة)
    ('إسطنبول', 'TR'): (41.0082, 28.9784),
    ('أنقرة', 'TR'): (39.9334, 32.8597),
    ('باريس', 'FR'): (48.8566, 2.3522),
    ('لندن', 'GB'): (51.5074, -0.1278),
    ('نيويورك', 'US'): (40.7128, -74.0060),
    ('موسكو', 'RU'): (55.7558, 37.6173),
    ('دلهي', 'IN'): (28.7041, 77.1025),
    ('بكين', 'CN'): (39.9042, 116.4074),
    ('طوكيو', 'JP'): (35.6762, 139.6503),
}


async def cleanup_locations():
    """تنظيف المواقع الخاطئة"""
    
    # الاتصال بقاعدة البيانات
    pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=1,
        max_size=5,
        command_timeout=60
    )
    
    try:
        async with pool.acquire() as conn:
            print("🔍 بدء تنظيف قاعدة البيانات...")
            print()
            
            # ========================================================================
            # 1. حذف المواقع الخاطئة
            # ========================================================================
            print("❌ حذف المواقع الخاطئة...")
            deleted_count = 0
            
            for name, country_code in LOCATIONS_TO_DELETE:
                try:
                    # أولاً: حذف الأحداث المرتبطة
                    await conn.execute(
                        """
                        DELETE FROM news_events 
                        WHERE location_id IN (
                            SELECT id FROM locations 
                            WHERE name = $1 AND country_code = $2
                        )
                        """,
                        name,
                        country_code
                    )
                    
                    # ثانياً: حذف المقاييس المرتبطة
                    await conn.execute(
                        """
                        DELETE FROM event_metrics 
                        WHERE event_id IN (
                            SELECT id FROM news_events 
                            WHERE location_id IN (
                                SELECT id FROM locations 
                                WHERE name = $1 AND country_code = $2
                            )
                        )
                        """,
                        name,
                        country_code
                    )
                    
                    # ثالثاً: حذف المكان
                    result = await conn.execute(
                        """
                        DELETE FROM locations 
                        WHERE name = $1 AND country_code = $2
                        """,
                        name,
                        country_code
                    )
                    
                    if result != "DELETE 0":
                        deleted_count += 1
                        print(f"  ✓ تم حذف: {name} ({country_code})")
                
                except Exception as e:
                    print(f"  ✗ خطأ في حذف {name} ({country_code}): {str(e)}")
            
            print(f"  المجموع: {deleted_count} موقع تم حذفه")
            print()
            
            # ========================================================================
            # 2. تصحيح الإحداثيات الخاطئة
            # ========================================================================
            print("✏️ تصحيح الإحداثيات الخاطئة...")
            fixed_count = 0
            
            for (name, country_code), (new_lat, new_lng) in LOCATIONS_TO_FIX.items():
                try:
                    result = await conn.execute(
                        """
                        UPDATE locations 
                        SET latitude = $1, longitude = $2
                        WHERE name = $3 AND country_code = $4
                        """,
                        new_lat,
                        new_lng,
                        name,
                        country_code
                    )
                    
                    if result != "UPDATE 0":
                        fixed_count += 1
                        print(f"  ✓ تم تصحيح: {name} ({country_code}) → ({new_lat}, {new_lng})")
                
                except Exception as e:
                    print(f"  ✗ خطأ في تصحيح {name} ({country_code}): {str(e)}")
            
            print(f"  المجموع: {fixed_count} موقع تم تصحيحه")
            print()
            
            # ========================================================================
            # 3. حذف المواقع بإحداثيات غير معقولة
            # ========================================================================
            print("🔍 البحث عن مواقع بإحداثيات غير معقولة...")
            
            # إحداثيات غير معقولة (مثل -9.9999999 أو 69.9999999)
            invalid_locations = await conn.fetch(
                """
                SELECT id, name, country_code, latitude, longitude
                FROM locations
                WHERE latitude < -90 OR latitude > 90
                   OR longitude < -180 OR longitude > 180
                   OR (latitude = -9.9999999 AND longitude = 69.9999999)
                   OR (latitude = 0 AND longitude = 0)
                """
            )
            
            if invalid_locations:
                print(f"  وجدت {len(invalid_locations)} موقع بإحداثيات غير معقولة:")
                
                for loc in invalid_locations:
                    try:
                        # حذف الأحداث والمقاييس أولاً
                        await conn.execute(
                            "DELETE FROM event_metrics WHERE event_id IN (SELECT id FROM news_events WHERE location_id = $1)",
                            loc['id']
                        )
                        await conn.execute(
                            "DELETE FROM news_events WHERE location_id = $1",
                            loc['id']
                        )
                        await conn.execute(
                            "DELETE FROM locations WHERE id = $1",
                            loc['id']
                        )
                        
                        print(f"    ✓ تم حذف: {loc['name']} ({loc['country_code']}) - إحداثيات: ({loc['latitude']}, {loc['longitude']})")
                    
                    except Exception as e:
                        print(f"    ✗ خطأ: {str(e)}")
            else:
                print("  ✓ لا توجد مواقع بإحداثيات غير معقولة")
            
            print()
            
            # ========================================================================
            # 4. إحصائيات نهائية
            # ========================================================================
            print("📊 الإحصائيات النهائية:")
            
            total_locations = await conn.fetchval("SELECT COUNT(*) FROM locations")
            total_events = await conn.fetchval("SELECT COUNT(*) FROM news_events")
            total_metrics = await conn.fetchval("SELECT COUNT(*) FROM event_metrics")
            
            print(f"  المواقع الكلية: {total_locations}")
            print(f"  الأحداث الكلية: {total_events}")
            print(f"  المقاييس الكلية: {total_metrics}")
            
            print()
            print("✅ تم إكمال التنظيف بنجاح!")
    
    finally:
        await pool.close()


if __name__ == "__main__":
    print("=" * 70)
    print("تنظيف قاعدة البيانات من المواقع الخاطئة")
    print("=" * 70)
    print()
    
    asyncio.run(cleanup_locations())
