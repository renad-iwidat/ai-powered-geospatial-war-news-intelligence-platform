#!/usr/bin/env python3
"""
Test cached forecasts
"""
import asyncio
import asyncpg
import sys
import os
from datetime import datetime
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings


async def test_cache():
    """Test reading cached forecasts"""
    
    print("=" * 80)
    print("🧪 Testing Cached Forecasts")
    print("=" * 80)
    
    conn = await asyncpg.connect(dsn=settings.DATABASE_URL)
    
    # Get all forecasts
    forecasts = await conn.fetch("""
        SELECT 
            id,
            forecast_type,
            days_ahead,
            generated_at,
            valid_until,
            forecast_data->>'trend' as trend,
            forecast_data->>'confidence_overall' as confidence,
            forecast_data->>'risk_level' as risk_level,
            forecast_data->>'overall_trend' as overall_trend
        FROM ai_forecasts
        ORDER BY generated_at DESC
    """)
    
    print(f"\n📊 Found {len(forecasts)} cached forecasts:\n")
    
    for f in forecasts:
        print(f"ID: {f['id']}")
        print(f"Type: {f['forecast_type']}")
        print(f"Generated: {f['generated_at']}")
        print(f"Valid Until: {f['valid_until']}")
        print(f"Days Ahead: {f['days_ahead']}")
        
        if f['trend']:
            print(f"Trend: {f['trend']}")
            print(f"Confidence: {f['confidence']}%")
            print(f"Risk Level: {f['risk_level']}")
        
        if f['overall_trend']:
            print(f"Overall Trend: {f['overall_trend']}")
        
        # Check if still valid
        now = datetime.now()
        valid_until = f['valid_until']
        is_valid = valid_until > now
        
        print(f"Status: {'✅ VALID' if is_valid else '❌ EXPIRED'}")
        print("-" * 80)
    
    # Test the cache query (same as API uses)
    print("\n🔍 Testing cache query (intelligence_forecast):\n")
    
    cached = await conn.fetchrow("""
        SELECT forecast_data, generated_at, valid_until
        FROM ai_forecasts
        WHERE forecast_type = $1
            AND valid_until > NOW()
        ORDER BY generated_at DESC
        LIMIT 1
    """, 'intelligence_forecast')
    
    if cached:
        print("✅ Cache HIT!")
        print(f"Generated: {cached['generated_at']}")
        print(f"Valid Until: {cached['valid_until']}")
        
        data = cached['forecast_data']
        if isinstance(data, str):
            data = json.loads(data)
        
        print(f"\nForecast Summary:")
        print(f"  Trend: {data.get('trend', 'N/A')}")
        print(f"  Confidence: {data.get('confidence_overall', 'N/A')}%")
        print(f"  Risk Level: {data.get('risk_level', 'N/A')}")
        
        if 'forecast' in data:
            print(f"  Predictions: {len(data['forecast'])} days")
        
        if 'summary' in data:
            summary_en = data['summary'].get('en', '')[:100]
            print(f"  Summary (EN): {summary_en}...")
    else:
        print("❌ Cache MISS - No valid forecast found")
    
    await conn.close()
    
    print("\n" + "=" * 80)
    print("✅ Test completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_cache())
