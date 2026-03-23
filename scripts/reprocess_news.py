#!/usr/bin/env python3
"""
Script to reprocess news articles after cleanup
إعادة معالجة الأخبار بعد التنظيف
"""

import asyncio
import asyncpg
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.geo.location_processor import process_locations
from app.services.extraction.metrics_processor import process_metrics


async def reprocess_news():
    """إعادة معالجة الأخبار"""
    
    # الاتصال بقاعدة البيانات
    pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=2,
        max_size=10,
        command_timeout=120
    )
    
    try:
        print("🔄 بدء إعادة معالجة الأخبار...")
        print()
        
        # ========================================================================
        # 1. حذف الأحداث والمقاييس القديمة
        # ========================================================================
        print("🗑️ حذف الأحداث والمقاييس القديمة...")
        
        async with pool.acquire() as conn:
            # حذف المقاييس
            metrics_deleted = await conn.fetchval(
                "SELECT COUNT(*) FROM event_metrics"
            )
            await conn.execute("DELETE FROM event_metrics")
            
            # حذف الأحداث
            events_deleted = await conn.fetchval(
                "SELECT COUNT(*) FROM news_events"
            )
            await conn.execute("DELETE FROM news_events")
            
            print(f"  ✓ تم حذف {metrics_deleted} مقياس")
            print(f"  ✓ تم حذف {events_deleted} حدث")
        
        print()
        
        # ========================================================================
        # 2. إعادة معالجة الأماكن
        # ========================================================================
        print("🌍 إعادة معالجة الأماكن...")
        
        batch_size = 100
        total_processed = 0
        total_places = 0
        total_locations = 0
        total_events = 0
        
        while True:
            result = await process_locations(pool, batch_size=batch_size)
            
            if result['processed_news'] == 0:
                break
            
            total_processed += result['processed_news']
            total_places += result['places_detected']
            total_locations += result['locations_upserted']
            total_events += result['events_created']
            
            print(f"  ✓ معالجة {result['processed_news']} خبر")
            print(f"    - أماكن مستخرجة: {result['places_detected']}")
            print(f"    - مواقع مخزنة: {result['locations_upserted']}")
            print(f"    - أحداث منشأة: {result['events_created']}")
        
        print()
        print(f"  المجموع:")
        print(f"    - أخبار معالجة: {total_processed}")
        print(f"    - أماكن مستخرجة: {total_places}")
        print(f"    - مواقع مخزنة: {total_locations}")
        print(f"    - أحداث منشأة: {total_events}")
        
        print()
        
        # ========================================================================
        # 3. إعادة معالجة المقاييس
        # ========================================================================
        print("📊 إعادة معالجة المقاييس...")
        
        total_events_processed = 0
        total_metrics_created = 0
        
        while True:
            result = await process_metrics(pool, batch_size=batch_size)
            
            if result['processed_events'] == 0:
                break
            
            total_events_processed += result['processed_events']
            total_metrics_created += result['metrics_created']
            
            print(f"  ✓ معالجة {result['processed_events']} حدث")
            print(f"    - مقاييس منشأة: {result['metrics_created']}")
        
        print()
        print(f"  المجموع:")
        print(f"    - أحداث معالجة: {total_events_processed}")
        print(f"    - مقاييس منشأة: {total_metrics_created}")
        
        print()
        
        # ========================================================================
        # 4. إحصائيات نهائية
        # ========================================================================
        print("📈 الإحصائيات النهائية:")
        
        async with pool.acquire() as conn:
            total_locations = await conn.fetchval("SELECT COUNT(*) FROM locations")
            total_events = await conn.fetchval("SELECT COUNT(*) FROM news_events")
            total_metrics = await conn.fetchval("SELECT COUNT(*) FROM event_metrics")
            
            # إحصائيات حسب الدول
            top_countries = await conn.fetch(
                """
                SELECT l.country_code, COUNT(DISTINCT ne.id) as event_count
                FROM locations l
                LEFT JOIN news_events ne ON l.id = ne.location_id
                GROUP BY l.country_code
                ORDER BY event_count DESC
                LIMIT 10
                """
            )
        
        print(f"  المواقع الكلية: {total_locations}")
        print(f"  الأحداث الكلية: {total_events}")
        print(f"  المقاييس الكلية: {total_metrics}")
        
        print()
        print("  أكثر 10 دول أحداثاً:")
        for row in top_countries:
            print(f"    - {row['country_code']}: {row['event_count']} حدث")
        
        print()
        print("✅ تم إكمال إعادة المعالجة بنجاح!")
    
    finally:
        await pool.close()


if __name__ == "__main__":
    print("=" * 70)
    print("إعادة معالجة الأخبار بعد التنظيف")
    print("=" * 70)
    print()
    
    asyncio.run(reprocess_news())
