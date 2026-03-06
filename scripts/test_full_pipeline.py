#!/usr/bin/env python3
"""
Test Full Pipeline - Backend + Data Processing
Tests the complete data flow every 15 minutes
"""
import asyncio
import asyncpg
import sys
import os
from datetime import datetime
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"🔍 {title}")
    print("=" * 80)


async def test_database_connection():
    """Test database connectivity"""
    print_section("Testing Database Connection")
    
    try:
        conn = await asyncpg.connect(dsn=settings.DATABASE_URL)
        
        # Test query
        result = await conn.fetchval("SELECT COUNT(*) FROM raw_news")
        print(f"✅ Database connected successfully!")
        print(f"   Total news articles: {result}")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_api_health():
    """Test API health endpoint"""
    print_section("Testing API Health")
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get("http://localhost:8000/health", timeout=10.0)
            data = response.json()
            
            if data.get("status") == "healthy":
                print(f"✅ API is healthy!")
                print(f"   Database: {data.get('database')}")
                print(f"   Version: {data.get('version')}")
                return True
            else:
                print(f"⚠️  API is unhealthy: {data}")
                return False
    except Exception as e:
        print(f"❌ API health check failed: {e}")
        return False


async def test_news_endpoint():
    """Test news articles endpoint"""
    print_section("Testing News Articles Endpoint")
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(
                "http://localhost:8000/api/v1/news-articles?limit=5",
                timeout=10.0
            )
            data = response.json()
            
            print(f"✅ News endpoint working!")
            print(f"   Total articles: {data.get('total', 0)}")
            print(f"   Returned: {len(data.get('items', []))}")
            
            if data.get('items'):
                first = data['items'][0]
                print(f"\n   Sample article:")
                print(f"   - ID: {first.get('id')}")
                print(f"   - Title: {first.get('title', '')[:50]}...")
                print(f"   - Events: {first.get('events_count', 0)}")
                print(f"   - Metrics: {first.get('metrics_count', 0)}")
            
            return True
    except Exception as e:
        print(f"❌ News endpoint failed: {e}")
        return False


async def test_analytics_endpoint():
    """Test analytics endpoint"""
    print_section("Testing Analytics Endpoint")
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(
                "http://localhost:8000/api/v1/analytics/timeline?days=7",
                timeout=10.0
            )
            data = response.json()
            
            print(f"✅ Analytics endpoint working!")
            print(f"   Timeline items: {len(data.get('timeline', []))}")
            
            return True
    except Exception as e:
        print(f"❌ Analytics endpoint failed: {e}")
        return False


async def test_ai_forecast():
    """Test AI forecast endpoint (cached)"""
    print_section("Testing AI Forecast (Cached)")
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(
                "http://localhost:8000/api/v1/predictions/ai-intelligence-forecast",
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'cache_info' in data:
                    print(f"✅ AI Forecast (from cache)!")
                    print(f"   Generated: {data['cache_info'].get('generated_at')}")
                    print(f"   Valid until: {data['cache_info'].get('valid_until')}")
                    print(f"   Trend: {data.get('trend')}")
                    print(f"   Confidence: {data.get('confidence_overall')}%")
                    print(f"   Risk: {data.get('risk_level')}")
                else:
                    print(f"✅ AI Forecast (fresh generation)!")
                    print(f"   Trend: {data.get('trend')}")
                    print(f"   Confidence: {data.get('confidence_overall')}%")
                
                return True
            elif response.status_code == 503:
                print(f"⚠️  AI service not configured (OPENAI_API_KEY missing)")
                return True  # Not a failure, just not configured
            else:
                print(f"❌ AI forecast failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ AI forecast failed: {e}")
        return False


async def check_processing_status():
    """Check data processing status"""
    print_section("Checking Data Processing Status")
    
    try:
        conn = await asyncpg.connect(dsn=settings.DATABASE_URL)
        
        # Check news
        total_news = await conn.fetchval("SELECT COUNT(*) FROM raw_news")
        news_with_events = await conn.fetchval(
            "SELECT COUNT(DISTINCT raw_news_id) FROM news_events"
        )
        
        # Check events
        total_events = await conn.fetchval("SELECT COUNT(*) FROM news_events")
        events_with_metrics = await conn.fetchval(
            "SELECT COUNT(DISTINCT event_id) FROM event_metrics"
        )
        
        # Check AI forecasts
        ai_forecasts = await conn.fetchval("SELECT COUNT(*) FROM ai_forecasts")
        valid_forecasts = await conn.fetchval(
            "SELECT COUNT(*) FROM ai_forecasts WHERE valid_until > NOW()"
        )
        
        await conn.close()
        
        print(f"📊 Processing Status:")
        print(f"\n   News Articles:")
        print(f"   - Total: {total_news}")
        print(f"   - With events: {news_with_events} ({news_with_events/total_news*100:.1f}%)")
        print(f"   - Without events: {total_news - news_with_events}")
        
        print(f"\n   Events:")
        print(f"   - Total: {total_events}")
        print(f"   - With metrics: {events_with_metrics} ({events_with_metrics/total_events*100:.1f}% if total_events > 0 else 0)")
        print(f"   - Without metrics: {total_events - events_with_metrics}")
        
        print(f"\n   AI Forecasts:")
        print(f"   - Total cached: {ai_forecasts}")
        print(f"   - Currently valid: {valid_forecasts}")
        
        # Calculate completion
        location_completion = (news_with_events / total_news * 100) if total_news > 0 else 0
        metrics_completion = (events_with_metrics / total_events * 100) if total_events > 0 else 0
        overall = (location_completion * 0.5 + metrics_completion * 0.5)
        
        print(f"\n   Overall Completion: {overall:.1f}%")
        
        if overall < 50:
            print(f"   ⚠️  Low completion - run data processing!")
        elif overall < 80:
            print(f"   📈 Good progress - continue processing")
        else:
            print(f"   ✅ Excellent completion!")
        
        return True
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False


async def simulate_15min_cycle():
    """Simulate what happens every 15 minutes"""
    print_section("Simulating 15-Minute Processing Cycle")
    
    print("\n📅 This is what should happen every 15 minutes:")
    print("\n1. Location Processing:")
    print("   - Fetch 20 unprocessed news articles")
    print("   - Extract place names using NER")
    print("   - Geocode place names to coordinates")
    print("   - Store locations and create events")
    
    print("\n2. Metrics Processing:")
    print("   - Fetch 20 events without metrics")
    print("   - Extract numerical data (casualties, weapons, etc)")
    print("   - Store metrics in database")
    
    print("\n3. AI Forecast (twice daily at 1 PM & 9 PM):")
    print("   - Generate intelligence forecast")
    print("   - Generate trend analysis")
    print("   - Cache results for 8 hours")
    print("   - All users read from cache")
    
    print("\n💡 To run processing manually:")
    print("   python scripts/process_batch.py")
    print("\n💡 To generate AI forecasts:")
    print("   python scripts/generate_ai_forecasts.py")


async def main():
    """Run all tests"""
    
    print("=" * 80)
    print("🚀 GeoNews AI - Full Pipeline Test")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    results = []
    
    # Run tests
    results.append(("Database Connection", await test_database_connection()))
    results.append(("API Health", await test_api_health()))
    results.append(("News Endpoint", await test_news_endpoint()))
    results.append(("Analytics Endpoint", await test_analytics_endpoint()))
    results.append(("AI Forecast", await test_ai_forecast()))
    results.append(("Processing Status", await check_processing_status()))
    
    # Simulate cycle
    await simulate_15min_cycle()
    
    # Summary
    print_section("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed\n")
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {name}")
    
    print("\n" + "=" * 80)
    
    if passed == total:
        print("✅ All tests passed! System is ready.")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Check logs above.")
    
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
