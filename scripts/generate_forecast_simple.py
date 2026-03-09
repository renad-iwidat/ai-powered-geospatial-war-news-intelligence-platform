#!/usr/bin/env python3
"""
Simple Forecast Generation Script
Run from project root: python scripts/generate_forecast_simple.py
"""

import asyncio
import sys
import os
import logging
from datetime import datetime, timedelta
import json

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function"""
    try:
        # Import after path is set
        import asyncpg
        from app.core.config import settings
        from app.services.predictions.llm_analyzer import IntelligenceAnalyzer
        
        logger.info("=" * 80)
        logger.info("🤖 AI Forecast Generation")
        logger.info("=" * 80)
        
        # Check config
        if not settings.DATABASE_URL:
            logger.error("❌ DATABASE_URL not set in .env")
            return False
        
        if not settings.OPENAI_API_KEY:
            logger.error("❌ OPENAI_API_KEY not set in .env")
            return False
        
        logger.info(f"✓ Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
        logger.info(f"✓ OpenAI API: configured")
        
        # Connect to database
        logger.info("\n📡 Connecting to database...")
        pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=1,
            max_size=2,
            command_timeout=120
        )
        
        try:
            # Test connection
            async with pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                logger.info(f"✓ Connected to PostgreSQL")
            
            # Generate intelligence forecast
            logger.info("\n" + "=" * 80)
            logger.info("1️⃣  Intelligence Forecast")
            logger.info("=" * 80)
            success_intel = await generate_intelligence_forecast(pool)
            
            # Generate trend analysis
            logger.info("\n" + "=" * 80)
            logger.info("2️⃣  Trend Analysis")
            logger.info("=" * 80)
            success_trend = await generate_trend_analysis(pool)
            
            # Summary
            logger.info("\n" + "=" * 80)
            if success_intel and success_trend:
                logger.info("✅ SUCCESS: All forecasts generated!")
                logger.info("=" * 80)
                return True
            else:
                logger.error("❌ FAILED: Some forecasts did not complete")
                logger.info("=" * 80)
                return False
        
        finally:
            await pool.close()
    
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}", exc_info=True)
        return False


async def generate_intelligence_forecast(pool):
    """Generate intelligence forecast"""
    try:
        from app.services.predictions.llm_analyzer import IntelligenceAnalyzer
        
        logger.info("Fetching historical data (60 days)...")
        
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
            logger.warning(f"⚠️  Not enough data ({len(rows)} days) - need at least 5 days")
            return False
        
        logger.info(f"✓ Found {len(rows)} days of data")
        
        historical_data = [
            {'date': row['date'].isoformat(), 'count': row['count']}
            for row in rows
        ]
        
        # Fetch recent articles
        logger.info("Fetching recent articles (7 days, max 20)...")
        
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
        
        logger.info(f"✓ Found {len(article_rows)} articles")
        
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
        logger.info("Calling OpenAI API (this may take 30-60 seconds)...")
        
        analyzer = IntelligenceAnalyzer()
        analysis = await analyzer.analyze_events_forecast(
            historical_data=historical_data,
            recent_articles=recent_articles,
            days_ahead=7
        )
        
        logger.info("✓ Analysis complete")
        logger.info(f"  • Risk Level: {analysis.get('risk_level', 'N/A')}")
        logger.info(f"  • Confidence: {analysis.get('confidence_overall', 'N/A')}%")
        logger.info(f"  • Trend: {analysis.get('trend', 'N/A')}")
        
        # Store in database
        logger.info("Storing in database...")
        
        valid_until = datetime.utcnow() + timedelta(hours=8)
        model_info = analysis.get('model_info', {})
        
        # Update existing or insert new
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
            await conn.execute(
                store_query,
                'intelligence_forecast',
                json.dumps(analysis),
                7,
                valid_until,
                json.dumps(model_info)
            )
        
        logger.info("✓ Stored successfully")
        logger.info(f"  • Valid until: {valid_until}")
        logger.info(f"  • Model: {model_info.get('model', 'N/A')}")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed: {str(e)}", exc_info=True)
        return False


async def generate_trend_analysis(pool):
    """Generate trend analysis"""
    try:
        from app.services.predictions.llm_analyzer import IntelligenceAnalyzer
        
        logger.info("Fetching historical data (30 days)...")
        
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
            logger.warning(f"⚠️  Not enough data ({len(rows)} days) - need at least 5 days")
            return False
        
        logger.info(f"✓ Found {len(rows)} days of data")
        
        historical_data = [
            {'date': row['date'].isoformat(), 'count': row['count']}
            for row in rows
        ]
        
        # Fetch recent articles
        logger.info("Fetching recent articles (3 days, max 10)...")
        
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
        
        logger.info(f"✓ Found {len(article_rows)} articles")
        
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
        logger.info("Calling OpenAI API (this may take 20-40 seconds)...")
        
        analyzer = IntelligenceAnalyzer()
        analysis = await analyzer.analyze_trend(
            historical_data=historical_data,
            recent_articles=recent_articles
        )
        
        logger.info("✓ Analysis complete")
        logger.info(f"  • Overall Trend: {analysis.get('overall_trend', 'N/A')}")
        logger.info(f"  • Trend Strength: {analysis.get('trend_strength', 'N/A')}%")
        logger.info(f"  • Confidence: {analysis.get('confidence_level', 'N/A')}%")
        
        # Store in database
        logger.info("Storing in database...")
        
        valid_until = datetime.utcnow() + timedelta(hours=8)
        model_info = analysis.get('model_info', {})
        
        # Update existing or insert new
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
            await conn.execute(
                store_query,
                'trend_analysis',
                json.dumps(analysis),
                30,
                valid_until,
                json.dumps(model_info)
            )
        
        logger.info("✓ Stored successfully")
        logger.info(f"  • Valid until: {valid_until}")
        logger.info(f"  • Model: {model_info.get('model', 'N/A')}")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
