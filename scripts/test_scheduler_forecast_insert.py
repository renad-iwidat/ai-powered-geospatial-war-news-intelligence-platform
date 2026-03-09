#!/usr/bin/env python3
"""
Test scheduler forecast insertion into ai_forecasts table
Verifies that both intelligence_forecast and trend_analysis are inserted correctly
"""

import asyncio
import asyncpg
import json
from datetime import datetime, timedelta
from app.core.config import settings


async def test_forecast_insertion():
    """Test inserting forecasts into ai_forecasts table"""
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        print("🧪 Testing AI Forecasts Table Insertion")
        print("=" * 80)
        
        # Sample intelligence forecast data
        intelligence_forecast = {
            "trend": "escalating",
            "summary": {
                "ar": "تشير البيانات إلى تصاعد كبير",
                "en": "The data indicates significant escalation"
            },
            "forecast": [
                {"date": "2026-03-07", "confidence": 80, "predicted_events": 330},
                {"date": "2026-03-08", "confidence": 75, "predicted_events": 290}
            ],
            "risk_level": "high",
            "confidence_overall": 70,
            "model_info": {
                "type": "OpenAI GPT Intelligence Analysis",
                "model": "gpt-4o",
                "analyzed_at": datetime.utcnow().isoformat(),
                "data_points": 6,
                "news_analyzed": 20
            }
        }
        
        # Sample trend analysis data
        trend_analysis = {
            "overall_trend": "escalating",
            "trend_strength": 85,
            "confidence_level": 80,
            "change_percentage": 530,
            "interpretation": {
                "ar": "تشير البيانات إلى زيادة كبيرة",
                "en": "The data indicates a significant increase"
            },
            "key_indicators": [
                "Increase in conflict event count",
                "Continued high count",
                "Recent news reports"
            ],
            "model_info": {
                "type": "OpenAI GPT Trend Analysis",
                "model": "gpt-4o",
                "analyzed_at": datetime.utcnow().isoformat(),
                "data_points": 6,
                "news_analyzed": 10
            }
        }
        
        valid_until = datetime.utcnow() + timedelta(hours=8)
        
        # Test 1: Insert intelligence forecast
        print("\n1️⃣  Testing Intelligence Forecast Insertion")
        print("-" * 80)
        
        try:
            await conn.execute("""
                INSERT INTO ai_forecasts 
                (forecast_type, forecast_data, days_ahead, generated_at, valid_until, model_info)
                VALUES ($1, $2, $3, NOW(), $4, $5)
            """,
                'intelligence_forecast',
                json.dumps(intelligence_forecast),
                7,
                valid_until,
                json.dumps(intelligence_forecast.get('model_info', {}))
            )
            print("✅ Intelligence forecast inserted successfully")
        except Exception as e:
            print(f"❌ Intelligence forecast insertion failed: {e}")
            return False
        
        # Test 2: Insert trend analysis
        print("\n2️⃣  Testing Trend Analysis Insertion")
        print("-" * 80)
        
        try:
            await conn.execute("""
                INSERT INTO ai_forecasts 
                (forecast_type, forecast_data, days_ahead, generated_at, valid_until, model_info)
                VALUES ($1, $2, $3, NOW(), $4, $5)
            """,
                'trend_analysis',
                json.dumps(trend_analysis),
                30,
                valid_until,
                json.dumps(trend_analysis.get('model_info', {}))
            )
            print("✅ Trend analysis inserted successfully")
        except Exception as e:
            print(f"❌ Trend analysis insertion failed: {e}")
            return False
        
        # Test 3: Verify data integrity
        print("\n3️⃣  Verifying Data Integrity")
        print("-" * 80)
        
        # Check intelligence forecast
        intel_record = await conn.fetchrow("""
            SELECT 
                id, forecast_type, days_ahead, generated_at, valid_until, 
                model_info, created_at,
                forecast_data->>'trend' as trend,
                forecast_data->>'risk_level' as risk_level
            FROM ai_forecasts
            WHERE forecast_type = 'intelligence_forecast'
            ORDER BY generated_at DESC
            LIMIT 1
        """)
        
        if intel_record:
            print("✅ Intelligence Forecast Record Found:")
            print(f"   ID: {intel_record['id']}")
            print(f"   Type: {intel_record['forecast_type']}")
            print(f"   Days Ahead: {intel_record['days_ahead']}")
            print(f"   Trend: {intel_record['trend']}")
            print(f"   Risk Level: {intel_record['risk_level']}")
            print(f"   Generated: {intel_record['generated_at']}")
            print(f"   Valid Until: {intel_record['valid_until']}")
            print(f"   Model Info: {intel_record['model_info']}")
            print(f"   Created: {intel_record['created_at']}")
        else:
            print("❌ Intelligence forecast record not found")
            return False
        
        # Check trend analysis
        trend_record = await conn.fetchrow("""
            SELECT 
                id, forecast_type, days_ahead, generated_at, valid_until,
                model_info, created_at,
                forecast_data->>'overall_trend' as overall_trend,
                forecast_data->>'trend_strength' as trend_strength
            FROM ai_forecasts
            WHERE forecast_type = 'trend_analysis'
            ORDER BY generated_at DESC
            LIMIT 1
        """)
        
        if trend_record:
            print("\n✅ Trend Analysis Record Found:")
            print(f"   ID: {trend_record['id']}")
            print(f"   Type: {trend_record['forecast_type']}")
            print(f"   Days Ahead: {trend_record['days_ahead']}")
            print(f"   Overall Trend: {trend_record['overall_trend']}")
            print(f"   Trend Strength: {trend_record['trend_strength']}")
            print(f"   Generated: {trend_record['generated_at']}")
            print(f"   Valid Until: {trend_record['valid_until']}")
            print(f"   Model Info: {trend_record['model_info']}")
            print(f"   Created: {trend_record['created_at']}")
        else:
            print("❌ Trend analysis record not found")
            return False
        
        # Test 4: Verify schema compliance
        print("\n4️⃣  Verifying Schema Compliance")
        print("-" * 80)
        
        # Check all required fields are populated
        checks = [
            ("forecast_type", intel_record['forecast_type'] == 'intelligence_forecast'),
            ("days_ahead", intel_record['days_ahead'] == 7),
            ("generated_at", intel_record['generated_at'] is not None),
            ("valid_until", intel_record['valid_until'] is not None),
            ("model_info", intel_record['model_info'] is not None),
            ("created_at", intel_record['created_at'] is not None),
        ]
        
        all_valid = True
        for field, valid in checks:
            status = "✅" if valid else "❌"
            print(f"{status} {field}: {'Present' if valid else 'Missing'}")
            if not valid:
                all_valid = False
        
        print("\n" + "=" * 80)
        if all_valid:
            print("✅ All tests passed! Schema is correct and data is properly inserted.")
        else:
            print("❌ Some tests failed. Please review the schema.")
        
        return all_valid
    
    finally:
        await conn.close()


if __name__ == "__main__":
    result = asyncio.run(test_forecast_insertion())
    exit(0 if result else 1)
