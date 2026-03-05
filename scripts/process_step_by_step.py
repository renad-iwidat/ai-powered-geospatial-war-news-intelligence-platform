"""
معالجة البيانات خطوة بخطوة
"""

import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000/api/v1/process"

async def process_locations_batch(batch_size=10):
    """معالجة دفعة من الأماكن"""
    async with httpx.AsyncClient(timeout=300.0, verify=False) as client:
        print(f"\n🔄 معالجة دفعة من الأماكن (حجم الدفعة: {batch_size})...")
        
        try:
            response = await client.post(
                f"{BASE_URL}/locations",
                json=batch_size  # إرسال الرقم مباشرة
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ نجحت المعالجة:")
                print(f"   • الأخبار المعالجة: {result.get('processed_news', 0)}")
                print(f"   • الأماكن المكتشفة: {result.get('places_detected', 0)}")
                print(f"   • الأماكن المخزنة: {result.get('locations_upserted', 0)}")
                print(f"   • الأحداث المنشأة: {result.get('events_created', 0)}")
                return result
            else:
                print(f"❌ خطأ: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return None


async def process_metrics_batch(batch_size=20):
    """معالجة دفعة من المؤشرات"""
    async with httpx.AsyncClient(timeout=300.0, verify=False) as client:
        print(f"\n🔄 استخراج المؤشرات (حجم الدفعة: {batch_size})...")
        
        try:
            response = await client.post(
                f"{BASE_URL}/metrics",
                json=batch_size  # إرسال الرقم مباشرة
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ نجح الاستخراج:")
                print(f"   • الأحداث المعالجة: {result.get('events_processed', 0)}")
                print(f"   • المؤشرات المستخرجة: {result.get('metrics_extracted', 0)}")
                return result
            else:
                print(f"❌ خطأ: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return None


async def get_stats():
    """الحصول على إحصائيات"""
    async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
        try:
            # عدد الأخبار
            response = await client.get("http://localhost:8000/api/v1/news/list?limit=1")
            if response.status_code == 200:
                total_news = response.json().get('total', 0)
            else:
                total_news = 0
            
            # عدد الأماكن
            response = await client.get("http://localhost:8000/api/v1/locations/places?limit=1000")
            if response.status_code == 200:
                total_places = len(response.json().get('items', []))
            else:
                total_places = 0
            
            return {
                'total_news': total_news,
                'total_places': total_places
            }
        except Exception as e:
            print(f"❌ خطأ في الإحصائيات: {e}")
            return None


async def main():
    print("=" * 80)
    print("🚀 معالجة البيانات خطوة بخطوة")
    print("=" * 80)
    
    # الإحصائيات الأولية
    print("\n📊 الإحصائيات الأولية:")
    stats = await get_stats()
    if stats:
        print(f"   • إجمالي الأخبار: {stats['total_news']}")
        print(f"   • إجمالي الأماكن: {stats['total_places']}")
    
    # ========================================================================
    # المرحلة 1: معالجة الأماكن
    # ========================================================================
    print("\n" + "=" * 80)
    print("📍 المرحلة 1: معالجة الأماكن")
    print("=" * 80)
    
    total_processed = 0
    total_events = 0
    batch_num = 1
    
    while True:
        print(f"\n--- دفعة #{batch_num} ---")
        result = await process_locations_batch(batch_size=10)
        
        if not result:
            print("❌ فشلت المعالجة، توقف")
            break
        
        processed = result.get('processed_news', 0)
        events = result.get('events_created', 0)
        
        total_processed += processed
        total_events += events
        
        if processed == 0:
            print("✅ انتهت معالجة جميع الأخبار!")
            break
        
        batch_num += 1
        
        # استراحة بين الدفعات
        print("⏳ انتظار 5 ثواني...")
        await asyncio.sleep(5)
    
    print(f"\n📊 ملخص المرحلة 1:")
    print(f"   • إجمالي الأخبار المعالجة: {total_processed}")
    print(f"   • إجمالي الأحداث المنشأة: {total_events}")
    
    # ========================================================================
    # المرحلة 2: استخراج المؤشرات
    # ========================================================================
    print("\n" + "=" * 80)
    print("📊 المرحلة 2: استخراج المؤشرات")
    print("=" * 80)
    
    total_events_processed = 0
    total_metrics = 0
    batch_num = 1
    
    while True:
        print(f"\n--- دفعة #{batch_num} ---")
        result = await process_metrics_batch(batch_size=20)
        
        if not result:
            print("❌ فشل الاستخراج، توقف")
            break
        
        events_proc = result.get('events_processed', 0)
        metrics = result.get('metrics_extracted', 0)
        
        total_events_processed += events_proc
        total_metrics += metrics
        
        if events_proc == 0:
            print("✅ انتهى استخراج جميع المؤشرات!")
            break
        
        batch_num += 1
        
        # استراحة بين الدفعات
        print("⏳ انتظار 3 ثواني...")
        await asyncio.sleep(3)
    
    print(f"\n📊 ملخص المرحلة 2:")
    print(f"   • إجمالي الأحداث المعالجة: {total_events_processed}")
    print(f"   • إجمالي المؤشرات المستخرجة: {total_metrics}")
    
    # الإحصائيات النهائية
    print("\n" + "=" * 80)
    print("📊 الإحصائيات النهائية:")
    print("=" * 80)
    stats = await get_stats()
    if stats:
        print(f"   • إجمالي الأخبار: {stats['total_news']}")
        print(f"   • إجمالي الأماكن: {stats['total_places']}")
    
    print("\n" + "=" * 80)
    print("✅ اكتملت المعالجة!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
