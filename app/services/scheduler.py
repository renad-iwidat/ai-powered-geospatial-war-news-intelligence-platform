"""
Background Task Scheduler
Handles periodic execution of data processing and AI forecast generation
Uses APScheduler with threading for parallel execution
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import httpx

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: Optional[BackgroundScheduler] = None
_scheduler_lock = asyncio.Lock()


class SchedulerManager:
    """Manages background task scheduling"""
    
    def __init__(self, api_base_url: str = "http://localhost:7235"):
        self.api_base_url = api_base_url
        self.scheduler = None
        self.is_running = False
    
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.scheduler = BackgroundScheduler(
            daemon=True,
            max_workers=2,  # 2 worker threads for parallel execution
            thread_pool_executor_kwargs={'max_workers': 2}
        )
        
        # Schedule data processing every 15 minutes
        self.scheduler.add_job(
            self._run_data_processing_sync,
            trigger=IntervalTrigger(minutes=15),
            id='data_processing_job',
            name='Data Processing (Location & Metrics Extraction)',
            replace_existing=True,
            max_instances=1,  # Prevent overlapping executions
            coalesce=True,
        )
        
        # Schedule AI forecast generation every 10 hours
        self.scheduler.add_job(
            self._run_ai_forecast_sync,
            trigger=IntervalTrigger(hours=10),
            id='ai_forecast_job',
            name='AI Forecast Generation',
            replace_existing=True,
            max_instances=1,  # Prevent overlapping executions
            coalesce=True,
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("✅ Scheduler started successfully")
        logger.info("📅 Jobs scheduled:")
        logger.info("   - Data Processing: Every 15 minutes")
        logger.info("   - AI Forecast: Every 10 hours")
    
    def stop(self):
        """Stop the scheduler"""
        if not self.is_running or not self.scheduler:
            logger.warning("Scheduler is not running")
            return
        
        self.scheduler.shutdown(wait=True)
        self.is_running = False
        logger.info("❌ Scheduler stopped")
    
    def _run_data_processing_sync(self):
        """Sync wrapper for async data processing"""
        asyncio.run(self._run_data_processing())
    
    def _run_ai_forecast_sync(self):
        """Sync wrapper for async AI forecast"""
        asyncio.run(self._run_ai_forecast())
    
    async def _run_data_processing(self):
        """Execute data processing tasks (location + metrics extraction)"""
        try:
            logger.info(f"🔄 Starting data processing at {datetime.now().isoformat()}")
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Extract locations (batch size: 50)
                try:
                    logger.info("  → Extracting locations from news articles...")
                    response = await client.post(
                        f"{self.api_base_url}/api/v1/data-processing/extract-locations",
                        json={"batch_size": 50}
                    )
                    response.raise_for_status()
                    location_result = response.json()
                    logger.info(f"  ✓ Locations extracted: {location_result.get('processed_count', 0)} articles processed")
                except Exception as e:
                    logger.error(f"  ✗ Location extraction failed: {str(e)}")
                
                # Extract metrics (batch size: 100)
                try:
                    logger.info("  → Extracting metrics from events...")
                    response = await client.post(
                        f"{self.api_base_url}/api/v1/data-processing/extract-metrics",
                        json={"batch_size": 100}
                    )
                    response.raise_for_status()
                    metrics_result = response.json()
                    logger.info(f"  ✓ Metrics extracted: {metrics_result.get('processed_count', 0)} events processed")
                except Exception as e:
                    logger.error(f"  ✗ Metrics extraction failed: {str(e)}")
            
            logger.info(f"✅ Data processing completed at {datetime.now().isoformat()}")
        
        except Exception as e:
            logger.error(f"❌ Data processing failed: {str(e)}")
    
    async def _run_ai_forecast(self):
        """Execute AI forecast generation"""
        try:
            logger.info(f"🤖 Starting AI forecast generation at {datetime.now().isoformat()}")
            
            # Import here to avoid circular imports
            import asyncpg
            from app.core.config import settings
            from app.services.predictions.llm_analyzer import IntelligenceAnalyzer
            
            # Connect to database
            pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=1,
                max_size=2,
                command_timeout=120
            )
            
            try:
                # Generate intelligence forecast
                try:
                    logger.info("  → Generating intelligence forecast...")
                    await self._generate_intelligence_forecast(pool)
                    logger.info(f"  ✓ Intelligence forecast generated")
                except Exception as e:
                    logger.error(f"  ✗ Intelligence forecast failed: {str(e)}")
                
                # Generate trend analysis
                try:
                    logger.info("  → Generating trend analysis...")
                    await self._generate_trend_analysis(pool)
                    logger.info(f"  ✓ Trend analysis generated")
                except Exception as e:
                    logger.error(f"  ✗ Trend analysis failed: {str(e)}")
                
                logger.info(f"✅ AI forecast generation completed at {datetime.now().isoformat()}")
            
            finally:
                await pool.close()
        
        except Exception as e:
            logger.error(f"❌ AI forecast generation failed: {str(e)}")
    
    async def _generate_intelligence_forecast(self, pool: asyncpg.Pool):
        """Generate and store intelligence forecast"""
        import json
        from app.services.predictions.llm_analyzer import IntelligenceAnalyzer
        from app.core.config import settings
        
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not configured - skipping intelligence forecast")
            return
        
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
            logger.warning(f"Not enough data ({len(rows)} days) for intelligence forecast")
            return
        
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
        analyzer = IntelligenceAnalyzer()
        analysis = await analyzer.analyze_events_forecast(
            historical_data=historical_data,
            recent_articles=recent_articles,
            days_ahead=7
        )
        
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
            await conn.execute(
                store_query,
                'intelligence_forecast',
                json.dumps(analysis),
                7,
                valid_until,
                json.dumps(model_info)
            )
        
        logger.info(f"    Risk Level: {analysis.get('risk_level', 'N/A')}")
        logger.info(f"    Confidence: {analysis.get('confidence_overall', 'N/A')}%")
    
    async def _generate_trend_analysis(self, pool: asyncpg.Pool):
        """Generate and store trend analysis"""
        import json
        from app.services.predictions.llm_analyzer import IntelligenceAnalyzer
        from app.core.config import settings
        
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not configured - skipping trend analysis")
            return
        
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
            logger.warning(f"Not enough data ({len(rows)} days) for trend analysis")
            return
        
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
        analyzer = IntelligenceAnalyzer()
        analysis = await analyzer.analyze_trend(
            historical_data=historical_data,
            recent_articles=recent_articles
        )
        
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
            await conn.execute(
                store_query,
                'trend_analysis',
                json.dumps(analysis),
                30,  # trend analysis covers 30 days of historical data
                valid_until,
                json.dumps(model_info)
            )
        
        logger.info(f"    Overall Trend: {analysis.get('overall_trend', 'N/A')}")
        logger.info(f"    Trend Strength: {analysis.get('trend_strength', 'N/A')}%")


# Global scheduler manager instance
_manager: Optional[SchedulerManager] = None


def get_scheduler_manager(api_base_url: str = "http://localhost:7235") -> SchedulerManager:
    """Get or create the global scheduler manager"""
    global _manager
    if _manager is None:
        _manager = SchedulerManager(api_base_url)
    return _manager


def start_scheduler(api_base_url: str = "http://localhost:7235"):
    """Start the background scheduler"""
    manager = get_scheduler_manager(api_base_url)
    manager.start()


def stop_scheduler():
    """Stop the background scheduler"""
    global _manager
    if _manager:
        _manager.stop()
        _manager = None
