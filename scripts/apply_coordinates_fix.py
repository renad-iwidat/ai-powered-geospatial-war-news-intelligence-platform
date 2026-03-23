#!/usr/bin/env python3
"""
Script to apply coordinates corrections to the database
تطبيق تصحيحات الإحداثيات على قاعدة البيانات
"""

import asyncio
import asyncpg
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings

# ============================================================================
# قائمة التصحيحات
# ============================================================================
COORDINATES_TO_FIX = {
    # (name, country_code): (new_lat, new_lng, reason)
    ('غزة', 'PS'): (31.5017, 34.4668, 'تصحيح الإحداثيات - كانت قرب الضفة'),
    ('عمّان', 'JO'): (31.9539, 35.9106, 'تحسين الدقة'),
}


async def apply_fixes():
    """تطبيق التصحيحات على قاعدة البيانات"""
    
    # الاتصال بقاعدة البيانات
    pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=1,
        max_size=5,
        command_timeout=60
    )
    
    try:
        print("=" * 70)
        print("تطبيق تصحيحات الإحداثيات على قاعدة البيانات")
        print("=" * 70)
        print()
        
        async with pool.acquire() as conn:
            # ========================================================================
            # 1. عرض الإحداثيات الحالية
            # ========================================================================
            print("📍 الإحداثيات الحالية:")
            print()
            
            for (name, country_code), (new_lat, new_lng, reason) in COORDINATES_TO_FIX.items():
                row = await conn.fetchrow(
                    "SELECT latitude, longitude FROM locations WHERE name = $1 AND country_code = $2",
                    name,
                    country_code
                )
                
                if row:
                    old_lat, old_lng = row['latitude'], row['longitude']
                    print(f"  {name} ({country_code}):")
                    print(f"    القديمة: ({old_lat}, {old_lng})")
                    print(f"    الجديدة: ({new_lat}, {new_lng})")
                    print(f"    السبب: {reason}")
                else:
                    print(f"  ⚠️ {name} ({country_code}): لم يتم العثور عليه في قاعدة البيانات")
                
                print()
            
            # ========================================================================
            # 2. تطبيق التصحيحات
            # ========================================================================
            print("✏️ تطبيق التصحيحات...")
            print()
            
            fixed_count = 0
            
            for (name, country_code), (new_lat, new_lng, reason) in COORDINATES_TO_FIX.items():
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
                        print(f"  ✅ تم تصحيح: {name} ({country_code})")
                        print(f"     الإحداثيات الجديدة: ({new_lat}, {new_lng})")
                    else:
                        print(f"  ⚠️ لم يتم العثور على: {name} ({country_code})")
                
                except Exception as e:
                    print(f"  ❌ خطأ في تصحيح {name} ({country_code}): {str(e)}")
                
                print()
            
            # ========================================================================
            # 3. التحقق من التصحيحات
            # ========================================================================
            print("🔍 التحقق من التصحيحات:")
            print()
            
            for (name, country_code), (new_lat, new_lng, reason) in COORDINATES_TO_FIX.items():
                row = await conn.fetchrow(
                    "SELECT latitude, longitude FROM locations WHERE name = $1 AND country_code = $2",
                    name,
                    country_code
                )
                
                if row:
                    lat, lng = row['latitude'], row['longitude']
                    if abs(lat - new_lat) < 0.0001 and abs(lng - new_lng) < 0.0001:
                        print(f"  ✅ {name} ({country_code}): تم التصحيح بنجاح")
                        print(f"     ({lat}, {lng})")
                    else:
                        print(f"  ❌ {name} ({country_code}): لم يتم التصحيح")
                        print(f"     المتوقع: ({new_lat}, {new_lng})")
                        print(f"     الفعلي: ({lat}, {lng})")
                else:
                    print(f"  ❌ {name} ({country_code}): لم يتم العثور عليه")
                
                print()
            
            # ========================================================================
            # 4. إحصائيات نهائية
            # ========================================================================
            print("📊 الإحصائيات:")
            print(f"  المواقع المصححة: {fixed_count}/{len(COORDINATES_TO_FIX)}")
            
            total_locations = await conn.fetchval("SELECT COUNT(*) FROM locations")
            print(f"  إجمالي المواقع في قاعدة البيانات: {total_locations}")
            
            print()
            print("✅ تم إكمال التصحيحات بنجاح!")
    
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(apply_fixes())
