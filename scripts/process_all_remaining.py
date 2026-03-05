"""
معالجة جميع البيانات المتبقية
"""

import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000/api/v1"

async def process_all():
    print("=" * 80)
    print("🚀 معالجة جميع البيانات المتبقية")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=300.0, verify=False) as client:
        
        # ====================================================================
        # المرحلة 1: معالجة الأماكن
        # ====================================================================
        print("\n" + "=" * 80)
        print("📍 المرحلة 1: استخراج الأماكن من الأخبار")
        print("=" * 80)
        
        total_processed = 0
        total_events = 0
        batch_num = 1
        
        while True:
            print(f"\n--- دفعة #{batch_num} ---")
            
            try:
                response = await client.post(
                    f"{BASE_URL}/data-processing/extract-locations",
                    json={"batch_size": 15}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    processed = result.get('processed_news', 0)
                    events = result.get('events_created', 0)
                    
                    print(f"✅ الأخبار المعالجة: {processed}")
                    print(f"✅ الأحداث المنشأة: {events}")
                    
                    total_processed += processed
                    total_events += events
                    
                    if processed == 0:
                        print("\n✅ انتهت معالجة جميع الأخبار!")
                        break
                    
                    batch_num += 1
                    print("⏳ انتظار 8 ثواني...")
                    await asyncio.sleep(8)
                    
                else:
                    print(f"❌ خطأ {response.status_code}: {response.text}")
                    break
                    
            except Exception as e:
                print(f"❌ خطأ: {e}")
                break
        
        print(f"\n📊 ملخص المرحلة 1:")
        print(f"   • إجمالي الأخبار المعالجة: {total_processed}")
        print(f"   • إجمالي الأحداث المنشأة: {total_events}")
        
        # ====================================================================
        # المرحلة 2: استخراج المؤشرات
        # ====================================================================
        print("\n" + "=" * 80)
        print("📊 المرحلة 2: استخراج المؤشرات من الأحداث")
        print("=" * 80)
        
        total_events_processed = 0
        total_metrics = 0
        batch_num = 1
        
        while True:
            print(f"\n--- دفعة #{batch_num} ---")
            
            try:
                response = await client.post(
                    f"{BASE_URL}/data-processing/extract-metrics",
                    json={"batch_size": 30}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    events_proc = result.get('events_processed', 0)
                    metrics = result.get('metrics_extracted', 0)
                    
                    print(f"✅ الأحداث المعالجة: {events_proc}")
                    print(f"✅ المؤشرات المستخرجة: {metrics}")
                    
                    total_events_processed += events_proc
                    total_metrics += metrics
                    
                    if events_proc == 0:
                        print("\n✅ انتهى استخراج جميع المؤشرات!")
                        break
                    
                    batch_num += 1
                    print("⏳ انتظار 3 ثواني...")
                    await asyncio.sleep(3)
                    
                else:
                    print(f"❌ خطأ {response.status_code}: {response.text}")
                    break
                    
            except Exception as e:
                print(f"❌ خطأ: {e}")
                break
        
        print(f"\n📊 ملخص المرحلة 2:")
        print(f"   • إجمالي الأحداث المعالجة: {total_events_processed}")
        print(f"   • إجمالي المؤشرات المستخرجة: {total_metrics}")
        
        # ====================================================================
        # الإحصائيات النهائية
        # ====================================================================
        print("\n" + "=" * 80)
        print("📊 الإحصائيات النهائية")
        print("=" * 80)
        
        try:
            response = await client.get(f"{BASE_URL}/data-processing/status")
            if response.status_code == 200:
                status = response.json()
                print(f"\n📰 الأخبار:")
                print(f"   • الإجمالي: {status['total_articles']}")
                print(f"   • مع أحداث: {status['articles_with_events']}")
                print(f"   • بدون أحداث: {status['articles_without_events']}")
                
                print(f"\n📍 الأحداث:")
                print(f"   • الإجمالي: {status['total_events']}")
                print(f"   • مع مؤشرات: {status['events_with_metrics']}")
                print(f"   • بدون مؤشرات: {status['events_without_metrics']}")
                
                print(f"\n✅ نسبة الإنجاز: {status['processing_completion_percentage']}%")
        except Exception as e:
            print(f"❌ خطأ في الإحصائيات: {e}")
    
    print("\n" + "=" * 80)
    print("✅ اكتملت المعالجة!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(process_all())
