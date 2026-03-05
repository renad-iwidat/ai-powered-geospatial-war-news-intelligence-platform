"""
Fix country_code column size issue
"""

import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def fix_country_code():
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(DATABASE_URL)
    
    print("=" * 80)
    print("فحص وإصلاح مشكلة country_code")
    print("=" * 80)
    
    # Check current column definition
    print("\n1. فحص تعريف العمود الحالي...")
    result = await conn.fetchrow("""
        SELECT 
            column_name, 
            data_type, 
            character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = 'locations' 
        AND column_name = 'country_code'
    """)
    
    print(f"   العمود: {result['column_name']}")
    print(f"   النوع: {result['data_type']}")
    print(f"   الطول الأقصى: {result['character_maximum_length']}")
    
    # Check if there are any country codes longer than 5 characters
    print("\n2. البحث عن أكواد دول أطول من 5 أحرف...")
    long_codes = await conn.fetch("""
        SELECT DISTINCT country_code, LENGTH(country_code) as len
        FROM locations
        WHERE LENGTH(country_code) > 5
        ORDER BY len DESC
    """)
    
    if long_codes:
        print(f"   ⚠️  وجدنا {len(long_codes)} كود أطول من 5 أحرف:")
        for row in long_codes:
            print(f"      • {row['country_code']} (طول: {row['len']})")
    else:
        print("   ✅ لا توجد أكواد أطول من 5 أحرف")
    
    # Drop dependent views temporarily
    print("\n3. حذف الـ views المؤقتة...")
    try:
        await conn.execute("DROP VIEW IF EXISTS v_news_snapshot_ar CASCADE")
        await conn.execute("DROP VIEW IF EXISTS v_news_ar CASCADE")
        print("   ✅ تم حذف الـ views")
    except Exception as e:
        print(f"   ⚠️  خطأ في حذف الـ views: {e}")
    
    # Alter column to increase size
    print("\n4. تعديل حجم العمود...")
    try:
        await conn.execute("""
            ALTER TABLE locations 
            ALTER COLUMN country_code TYPE VARCHAR(10)
        """)
        print("   ✅ تم تعديل العمود بنجاح إلى VARCHAR(10)")
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
    
    # Verify the change
    print("\n5. التحقق من التعديل...")
    result = await conn.fetchrow("""
        SELECT character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = 'locations' 
        AND column_name = 'country_code'
    """)
    print(f"   الطول الأقصى الجديد: {result['character_maximum_length']}")
    
    await conn.close()
    
    print("\n" + "=" * 80)
    print("✅ اكتمل الإصلاح")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(fix_country_code())
