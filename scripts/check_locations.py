#!/usr/bin/env python3
"""
Script to check existing locations in database
التحقق من المواقع الموجودة في قاعدة البيانات
"""

import asyncio
import asyncpg
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


async def check_locations():
    """التحقق من المواقع الموجودة"""
    
    # الاتصال بقاعدة البيانات
    pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=1,
        max_size=5,
        command_timeout=60
    )
    
    try:
        print("=" * 70)
        print("المواقع الموجودة في قاعدة البيانات")
        print("=" * 70)
        print()
        
        async with pool.acquire() as conn:
            # ========================================================================
            # 1. عدد المواقع الكلي
            # ========================================================================
            total = await conn.fetchval("SELECT COUNT(*) FROM locations")
            print(f"📊 إجمالي المواقع: {total}")
            print()
            
            # ========================================================================
            # 2. المواقع الفلسطينية
            # ========================================================================
            print("🇵🇸 المواقع الفلسطينية (PS):")
            ps_locations = await conn.fetch(
                "SELECT id, name, latitude, longitude FROM locations WHERE country_code = 'PS' ORDER BY name"
            )
            
            if ps_locations:
                for loc in ps_locations:
                    print(f"  - {loc['name']}: ({loc['latitude']}, {loc['longitude']})")
            else:
                print("  لا توجد مواقع فلسطينية")
            
            print()
            
            # ========================================================================
            # 3. المواقع الأردنية
            # ========================================================================
            print("🇯🇴 المواقع الأردنية (JO):")
            jo_locations = await conn.fetch(
                "SELECT id, name, latitude, longitude FROM locations WHERE country_code = 'JO' ORDER BY name"
            )
            
            if jo_locations:
                for loc in jo_locations:
                    print(f"  - {loc['name']}: ({loc['latitude']}, {loc['longitude']})")
            else:
                print("  لا توجد مواقع أردنية")
            
            print()
            
            # ========================================================================
            # 4. البحث عن أسماء مشابهة
            # ========================================================================
            print("🔍 البحث عن أسماء مشابهة:")
            
            # البحث عن غزة
            gaza_search = await conn.fetch(
                "SELECT id, name, country_code, latitude, longitude FROM locations WHERE name ILIKE '%غزة%' OR name ILIKE '%gaza%'"
            )
            
            if gaza_search:
                print("  غزة:")
                for loc in gaza_search:
                    print(f"    - {loc['name']} ({loc['country_code']}): ({loc['latitude']}, {loc['longitude']})")
            else:
                print("  ❌ لم يتم العثور على غزة")
            
            print()
            
            # البحث عن عمّان
            amman_search = await conn.fetch(
                "SELECT id, name, country_code, latitude, longitude FROM locations WHERE name ILIKE '%عمّان%' OR name ILIKE '%عمان%' OR name ILIKE '%amman%'"
            )
            
            if amman_search:
                print("  عمّان:")
                for loc in amman_search:
                    print(f"    - {loc['name']} ({loc['country_code']}): ({loc['latitude']}, {loc['longitude']})")
            else:
                print("  ❌ لم يتم العثور على عمّان")
            
            print()
            
            # ========================================================================
            # 5. أكثر 20 موقع
            # ========================================================================
            print("📍 أول 20 موقع في قاعدة البيانات:")
            top_locations = await conn.fetch(
                "SELECT id, name, country_code, latitude, longitude FROM locations ORDER BY id LIMIT 20"
            )
            
            for loc in top_locations:
                print(f"  {loc['id']:4d}. {loc['name']:20s} ({loc['country_code']}): ({loc['latitude']}, {loc['longitude']})")
    
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(check_locations())
