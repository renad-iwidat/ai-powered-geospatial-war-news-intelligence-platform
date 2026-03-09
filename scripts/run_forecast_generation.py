#!/usr/bin/env python3
"""
Run AI Forecast Generation Manually
Generates both intelligence_forecast and trend_analysis
"""

import asyncio
import sys
import logging
from datetime import datetime, timedelta
import json
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_forecast_generation():
    """Run forecast generation manually"""
    
    try:
        import asyncpg
        from app.core.config import settings
        from app.services.predictions.llm_analyzer import IntelligenceAnalyzer
        
        if not settings.OPENAI_API_KEY:
            logger.error("❌ OPENAI_API_KEY not configured in .env")
            return False
        
        logger.info("🤖 Starting AI Forecast Generation")
        logger.info("=" * 80)
        
        # Connect to database
        logger.info("📡 Connecting to database...")
        pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=1,
            max_size=2,
            command_timeout=120
        )
        
        try:
            # Generate intelligence forecast
            logger.info("\n1️⃣  Generating Intelligence Forecast...")
            logger.info("-" * 80)
            success_intel = await generate_intelligence_forecast(pool)
            
            # Generate trend analysis
            logger.info("\n2️⃣  Generating Trend Analysis...")
            logger.info("-" * 80)
            success_trend = await generate_trend_analysis(pool)
            
            logger.info("\n" + "=" * 80)
            if success_intel and success_trend:
                logger.info("✅ All forecasts generated successfully!")
                return True
            else:
                logger.error("❌ Some forecasts failed to generate")
                return False
        
        finally:
            await pool.close()
    
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}", exc_info=True)
        return False


async def generate_intelligence_forecast(pool):
    """Generate and store intelligence forecast"""
    try:
        import asyncpg
        from app.services.predictions.llm_analyzer import IntelligenceAnalyzer
        
        # Fetch historical data
        query = """
            SELECT
                DATE(COALESCE(rn.published_at, rn.fetched_at)) as date,
                COUNT(DISTINCT ne.id) as count
            FROM raw_news rn
            LEFT JOIN news_events ne ON rn.id = ne.raw_news_id
            WHERE COALESCE(rn.published_at, rn.fetched_at) >= CURRENT_DATE - INTERVAL '60 days'
            GROUP BY DATE(COALESCE(rn.published_at, rn.fetched_at))
            ORDER BY date ASC
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
        
        if len(rows) < 5:
            logger.warning(f"⚠️  Not enough data ({len(rows)} days) for intelligence forecast")
            return False
        
        logger.info(f"📊 Found {len(rows)} days of historical data")
        
        historical_data = [
            {'date': row['date'].isoformat(), 'count': row['count']}
            for row in rows
        ]
        
        # Fetch recent articles
        articles_query = """
            SELECT
                rn.title_original as title,
                rn.content_original as content,
                rn.published_at,
                s.name as source_name
            FROM raw_news rn
            LEFT JOIN sources s ON rn.source_id = s.id
            WHERE COALESCE(rn.published_at, rn.fetched_at) >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC
            LIMIT 20
        """
        
        async with pool.acquire() as conn:
            article_rows = await conn.fetch(articles_query)
        
        logger.info(f"📰 Found {len(article_rows)} recent articles")
        
        recent_articles = [
            {
                'title': row['title'],
                'content': row['content'][:500] if row['content'] else '',
                'published_at': row['published_at'].isoformat() if row['published_at'] else 'Unknown',
                'source': row['source_name']
            }
            for row in article_rows
        ]
        
        # Generate forecast
        logger.info("🔄 Calling OpenAI API for intelligence analysis...")
        analyzer = IntelligenceAnalyzer()
        analysis = await analyzer.analyze_events_forecast(
            historical_data=historical_data,
            recent_articles=recent_articles,
            days_ahead=7
        )
        
        logger.info(f"✓ Analysis complete")
        logger.info(f"  Risk Level: {analysis.get('risk_level', 'N/A')}")
        logger.info(f"  Confidence: {analysis.get('confidence_overall', 'N/A')}%")
        logger.info(f"  Trend: {analysis.get('trend', 'N/A')}")
        
        # Store in database
        valid_until = datetime.utcnow() + timedelta(hours=8)
        model_info = analysis.get('model_info', {})
        
        store_query = """
            INSERT INTO ai_forecasts 
            (forecast_type, forecast_data, days_ahead, generated_at, valid_until, model_info)
            VALUES ($1, $2, $3, NOW(), $4, $5)
            ON CONFLICT (forecast_type) DO UPDATE SET
                forecast_data = EXCLUDED.forecast_data,
                days_ahead = EXCLUDED.days_ahead,
                generated_at = NOW(),
                valid_until = EXCLUDED.valid_until,
                model_info = EXCLUDED.model_info
        """
        
        async with pool.acquire() as conn:
            result = await conn.execute(
                store_query,
                'intelligence_forecast',
                json.dumps(analysis),
                7,
                valid_until,
                json.dumps(model_info)
            )
        
        logger.info(f"💾 Stored in database")
        logger.info(f"  Valid Until: {valid_until}")
        logger.info(f"  Model: {model_info.get('model', 'N/A')}")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Intelligence forecast failed: {str(e)}", exc_info=True)
        return False


async def generate_trend_analysis(pool):
    """Generate and store trend analysis"""
    try:
        import asyncpg
        from app.services.predictions.llm_analyzer import IntelligenceAnalyzer
        
        # Fetch historical data
        query = """
            SELECT
                DATE(COALESCE(rn.published_at, rn.fetched_at)) as date,
                COUNT(DISTINCT ne.id) as count
            FROM raw_news rn
            LEFT JOIN news_events ne ON rn.id = ne.raw_news_id
            WHERE COALESCE(rn.published_at, rn.fetched_at) >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY DATE(COALESCE(rn.published_at, rn.fetched_at))
            ORDER BY date ASC
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
        
        if len(rows) < 5:
            logger.warning(f"⚠️  Not enough data ({len(rows)} days) for trend analysis")
            return False
        
        logger.info(f"📊 Found {len(rows)} days of historical data")
        
        historical_data = [
            {'date': row['date'].isoformat(), 'count': row['count']}
            for row in rows
        ]
        
        # Fetch recent articles
        articles_query = """
            SELECT
                rn.title_original as title,
                rn.content_original as content,
                rn.published_at,
                s.name as source_name
            FROM raw_news rn
            LEFT JOIN sources s ON rn.source_id = s.id
            WHERE COALESCE(rn.published_at, rn.fetched_at) >= CURRENT_DATE - INTERVAL '3 days'
            ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC
            LIMIT 10
        """
        
        async with pool.acquire() as conn:
            article_rows = await conn.fetch(articles_query)
        
        logger.info(f"📰 Found {len(article_rows)} recent articles")
        
        recent_articles = [
            {
                'title': row['title'],
                'content': row['content'][:500] if row['content'] else '',
                'published_at': row['published_at'].isoformat() if row['published_at'] else 'Unknown',
                'source': row['source_name']
            }
            for row in article_rows
        ]
        
        # Generate analysis
        logger.info("🔄 Calling OpenAI API for trend analysis...")
        analyzer = IntelligenceAnalyzer()
        analysis = await analyzer.analyze_trend(
            historical_data=historical_data,
            recent_articles=recent_articles
        )
        
        logger.info(f"✓ Analysis complete")
        logger.info(f"  Overall Trend: {analysis.get('overall_trend', 'N/A')}")
        logger.info(f"  Trend Strength: {analysis.get('trend_strength', 'N/A')}%")
        logger.info(f"  Confidence: {analysis.get('confidence_level', 'N/A')}%")
        
        # Store in database
        valid_until = datetime.utcnow() + timedelta(hours=8)
        model_info = analysis.get('model_info', {})
        
        store_query = """
            INSERT INTO ai_forecasts 
            (forecast_type, forecast_data, days_ahead, generated_at, valid_until, model_info)
            VALUES ($1, $2, $3, NOW(), $4, $5)
            ON CONFLICT (forecast_type) DO UPDATE SET
                forecast_data = EXCLUDED.forecast_data,
                days_ahead = EXCLUDED.days_ahead,
                generated_at = NOW(),
                valid_until = EXCLUDED.valid_until,
                model_info = EXCLUDED.model_info
        """
        
        async with pool.acquire() as conn:
            result = await conn.execute(
                store_query,
                'trend_analysis',
                json.dumps(analysis),
                30,
                valid_until,
                json.dumps(model_info)
            )
        
        logger.info(f"💾 Stored in database")
        logger.info(f"  Valid Until: {valid_until}")
        logger.info(f"  Model: {model_info.get('model', 'N/A')}")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Trend analysis failed: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    result = asyncio.run(run_forecast_generation())
    sys.exit(0 if result else 1)
