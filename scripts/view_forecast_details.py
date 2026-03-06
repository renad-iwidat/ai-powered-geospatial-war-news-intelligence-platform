#!/usr/bin/env python3
"""
View detailed forecast analysis
"""
import asyncio
import asyncpg
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings


async def view_latest_forecast():
    """View latest intelligence forecast in detail"""
    
    print("=" * 80)
    print("🤖 Latest AI Intelligence Forecast (GPT-4o)")
    print("=" * 80)
    
    conn = await asyncpg.connect(dsn=settings.DATABASE_URL)
    
    # Get latest intelligence forecast
    row = await conn.fetchrow("""
        SELECT forecast_data, generated_at, valid_until
        FROM ai_forecasts
        WHERE forecast_type = 'intelligence_forecast'
            AND valid_until > NOW()
        ORDER BY generated_at DESC
        LIMIT 1
    """)
    
    if not row:
        print("❌ No valid forecast found")
        await conn.close()
        return
    
    data = row['forecast_data']
    if isinstance(data, str):
        data = json.loads(data)
    
    print(f"\n⏰ Generated: {row['generated_at']}")
    print(f"⏰ Valid Until: {row['valid_until']}")
    print(f"🤖 Model: {data.get('model_info', {}).get('model', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("📊 FORECAST SUMMARY")
    print("=" * 80)
    
    print(f"\n📈 Trend: {data.get('trend', 'N/A')}")
    print(f"🎯 Overall Confidence: {data.get('confidence_overall', 'N/A')}%")
    print(f"⚠️  Risk Level: {data.get('risk_level', 'N/A')}")
    
    print("\n" + "-" * 80)
    print("🔮 DAILY PREDICTIONS")
    print("-" * 80)
    
    if 'forecast' in data:
        for day in data['forecast']:
            print(f"  {day.get('date', 'N/A')}: {day.get('predicted_events', 'N/A')} events (confidence: {day.get('confidence', 'N/A')}%)")
    
    print("\n" + "-" * 80)
    print("🔑 KEY FACTORS")
    print("-" * 80)
    
    if 'key_factors' in data:
        for i, factor in enumerate(data['key_factors'], 1):
            print(f"  {i}. {factor}")
    
    print("\n" + "-" * 80)
    print("📝 SUMMARY (English)")
    print("-" * 80)
    
    if 'summary' in data:
        summary_en = data['summary'].get('en', 'N/A')
        # Word wrap
        words = summary_en.split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 <= 76:
                line += word + " "
            else:
                print(f"  {line}")
                line = word + " "
        if line:
            print(f"  {line}")
    
    print("\n" + "-" * 80)
    print("📝 الملخص (عربي)")
    print("-" * 80)
    
    if 'summary' in data:
        summary_ar = data['summary'].get('ar', 'غير متوفر')
        print(f"  {summary_ar}")
    
    print("\n" + "-" * 80)
    print("💡 INSIGHTS (English)")
    print("-" * 80)
    
    if 'insights' in data:
        insights_en = data['insights'].get('en', 'N/A')
        words = insights_en.split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 <= 76:
                line += word + " "
            else:
                print(f"  {line}")
                line = word + " "
        if line:
            print(f"  {line}")
    
    print("\n" + "-" * 80)
    print("💡 الرؤى (عربي)")
    print("-" * 80)
    
    if 'insights' in data:
        insights_ar = data['insights'].get('ar', 'غير متوفر')
        print(f"  {insights_ar}")
    
    print("\n" + "-" * 80)
    print("⚠️  RISK ASSESSMENT")
    print("-" * 80)
    
    if 'highest_risk_day' in data:
        hrd = data['highest_risk_day']
        print(f"  Highest Risk: {hrd.get('date', 'N/A')} - {hrd.get('reason', 'N/A')}")
    
    if 'lowest_activity_day' in data:
        lad = data['lowest_activity_day']
        print(f"  Lowest Activity: {lad.get('date', 'N/A')} - {lad.get('reason', 'N/A')}")
    
    # Check for data quality note
    if 'data_quality_note' in data:
        print("\n" + "-" * 80)
        print("📊 DATA QUALITY")
        print("-" * 80)
        print(f"  EN: {data['data_quality_note'].get('en', 'N/A')}")
        print(f"  AR: {data['data_quality_note'].get('ar', 'غير متوفر')}")
    
    print("\n" + "=" * 80)
    print("✅ Forecast Details Complete")
    print("=" * 80)
    
    await conn.close()


if __name__ == "__main__":
    asyncio.run(view_latest_forecast())
