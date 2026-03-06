#!/usr/bin/env python3
"""
Generate AI Forecasts and Cache Them
Runs twice daily to generate and store AI analysis
"""
import asyncio
import asyncpg
import sys
import os
from datetime import datetime, timedelta
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings
from app.services.predictions.llm_analyzer import IntelligenceAnalyzer


async def fetch_historical_data(pool: asyncpg.Pool, days: int = 60):
    """Fetch historical events data"""
    query = """
        SELECT
            DATE(COALESCE(rn.published_at, rn.fetched_at)) as date,
            COUNT(DISTINCT ne.id) as count
        FROM raw_news rn
        LEFT JOIN news_events ne ON rn.id = ne.raw_news_id
        WHERE COALESCE(rn.published_at, rn.fetched_at) >= CURRENT_DATE - INTERVAL '%s days'
        GROUP BY DATE(COALESCE(rn.published_at, rn.fetched_at))
        ORDER BY date DESC
    """ % days
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
    
    return [
        {'date': row['date'].isoformat(), 'count': row['count']}
        for row in rows
    ]


async def fetch_recent_articles(pool: asyncpg.Pool, days: int = 7):
    """Fetch recent articles for context"""
    query = """
        SELECT
            rn.title_original as title,
            rn.content_original as content,
            rn.published_at,
            s.name as source_name
        FROM raw_news rn
        LEFT JOIN sources s ON rn.source_id = s.id
        WHERE COALESCE(rn.published_at, rn.fetched_at) >= CURRENT_DATE - INTERVAL '%s days'
        ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC
        LIMIT 20
    """ % days
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
    
    return [
        {
            'title': row['title'],
            'content': row['content'][:500] if row['content'] else '',
            'published_at': row['published_at'].isoformat() if row['published_at'] else 'Unknown',
            'source': row['source_name']
        }
        for row in rows
    ]


async def store_forecast(
    pool: asyncpg.Pool,
    forecast_type: str,
    forecast_data: dict,
    days_ahead: int = None,
    valid_hours: int = 8
):
    """Store forecast in database"""
    
    valid_until = datetime.utcnow() + timedelta(hours=valid_hours)
    
    query = """
        INSERT INTO ai_forecasts 
        (forecast_type, forecast_data, days_ahead, generated_at, valid_until, model_info)
        VALUES ($1, $2, $3, NOW(), $4, $5)
        RETURNING id
    """
    
    model_info = forecast_data.get('model_info', {})
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            query,
            forecast_type,
            json.dumps(forecast_data),
            days_ahead,
            valid_until,
            json.dumps(model_info)
        )
    
    return row['id']


async def generate_intelligence_forecast(pool: asyncpg.Pool, days_ahead: int = 7):
    """Generate AI intelligence forecast"""
    
    print(f"\n🤖 Generating AI Intelligence Forecast ({days_ahead} days)...")
    
    try:
        # Check if OpenAI API key is configured
        if not settings.OPENAI_API_KEY:
            print("⚠️  OPENAI_API_KEY not configured - skipping AI forecast")
            return None
        
        # Fetch data
        historical_data = await fetch_historical_data(pool, days=60)
        recent_articles = await fetch_recent_articles(pool, days=7)
        
        if len(historical_data) < 5:
            print(f"⚠️  Not enough data ({len(historical_data)} days) - need at least 5 days")
            return None
        
        print(f"   📊 Historical data: {len(historical_data)} days")
        print(f"   📰 Recent articles: {len(recent_articles)} articles")
        
        # Generate AI analysis
        analyzer = IntelligenceAnalyzer()
        analysis = await analyzer.analyze_events_forecast(
            historical_data=historical_data,
            recent_articles=recent_articles,
            days_ahead=days_ahead
        )
        
        # Store in database
        forecast_id = await store_forecast(
            pool,
            forecast_type='intelligence_forecast',
            forecast_data=analysis,
            days_ahead=days_ahead,
            valid_hours=8  # Valid for 8 hours (until next run)
        )
        
        print(f"   ✅ Forecast generated and stored (ID: {forecast_id})")
        print(f"   📈 Trend: {analysis.get('trend', 'N/A')}")
        print(f"   🎯 Confidence: {analysis.get('confidence_overall', 'N/A')}%")
        print(f"   ⚠️  Risk Level: {analysis.get('risk_level', 'N/A')}")
        
        return forecast_id
        
    except Exception as e:
        print(f"   ❌ Error generating forecast: {e}")
        import traceback
        traceback.print_exc()
        return None


async def generate_trend_analysis(pool: asyncpg.Pool):
    """Generate AI trend analysis"""
    
    print(f"\n📊 Generating AI Trend Analysis...")
    
    try:
        if not settings.OPENAI_API_KEY:
            print("⚠️  OPENAI_API_KEY not configured - skipping trend analysis")
            return None
        
        # Fetch data
        historical_data = await fetch_historical_data(pool, days=30)
        recent_articles = await fetch_recent_articles(pool, days=3)
        
        if len(historical_data) < 5:
            print(f"⚠️  Not enough data ({len(historical_data)} days)")
            return None
        
        print(f"   📊 Historical data: {len(historical_data)} days")
        print(f"   📰 Recent articles: {len(recent_articles)} articles")
        
        # Generate analysis
        analyzer = IntelligenceAnalyzer()
        analysis = await analyzer.analyze_trend(
            historical_data=historical_data,
            recent_articles=recent_articles
        )
        
        # Store in database
        forecast_id = await store_forecast(
            pool,
            forecast_type='trend_analysis',
            forecast_data=analysis,
            valid_hours=8
        )
        
        print(f"   ✅ Trend analysis stored (ID: {forecast_id})")
        print(f"   📈 Overall Trend: {analysis.get('overall_trend', 'N/A')}")
        print(f"   💪 Trend Strength: {analysis.get('trend_strength', 'N/A')}%")
        
        return forecast_id
        
    except Exception as e:
        print(f"   ❌ Error generating trend analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


async def cleanup_old_forecasts(pool: asyncpg.Pool, keep_days: int = 7):
    """Delete old forecasts to keep database clean"""
    
    print(f"\n🧹 Cleaning up old forecasts (older than {keep_days} days)...")
    
    query = """
        DELETE FROM ai_forecasts
        WHERE generated_at < NOW() - INTERVAL '%s days'
        RETURNING id
    """ % keep_days
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
    
    print(f"   ✅ Deleted {len(rows)} old forecasts")


async def main():
    """Main function"""
    
    print("=" * 80)
    print("🤖 AI Forecast Generator")
    print(f"⏰ Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Connect to database
    pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=2,
        max_size=5,
        command_timeout=120
    )
    
    try:
        # Generate forecasts
        await generate_intelligence_forecast(pool, days_ahead=7)
        await generate_trend_analysis(pool)
        
        # Cleanup old data
        await cleanup_old_forecasts(pool, keep_days=7)
        
        print("\n" + "=" * 80)
        print("✅ All forecasts generated successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
