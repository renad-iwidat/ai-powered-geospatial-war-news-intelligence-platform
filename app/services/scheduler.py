"""
Background Task Scheduler
Handles periodic execution of data processing and AI forecast generation
Uses APScheduler with threading for parallel execution
"""

import logging
import asyncio
from datetime import datetime
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
            
            async with httpx.AsyncClient(timeout=600.0) as client:
                try:
                    logger.info("  → Generating intelligence forecast...")
                    response = await client.get(
                        f"{self.api_base_url}/api/v1/predictions/intelligence-forecast",
                        params={"days": 7, "force_refresh": True}
                    )
                    response.raise_for_status()
                    forecast_result = response.json()
                    logger.info(f"  ✓ Intelligence forecast generated")
                    logger.info(f"    Risk Level: {forecast_result.get('risk_level', 'N/A')}")
                    logger.info(f"    Confidence: {forecast_result.get('confidence_overall', 'N/A')}%")
                except Exception as e:
                    logger.error(f"  ✗ Intelligence forecast failed: {str(e)}")
                
                try:
                    logger.info("  → Generating trend analysis...")
                    response = await client.get(
                        f"{self.api_base_url}/api/v1/predictions/trend-analysis"
                    )
                    response.raise_for_status()
                    trend_result = response.json()
                    logger.info(f"  ✓ Trend analysis generated")
                    logger.info(f"    Overall Trend: {trend_result.get('overall_trend', 'N/A')}")
                    logger.info(f"    Trend Strength: {trend_result.get('trend_strength', 'N/A')}%")
                except Exception as e:
                    logger.error(f"  ✗ Trend analysis failed: {str(e)}")
            
            logger.info(f"✅ AI forecast generation completed at {datetime.now().isoformat()}")
        
        except Exception as e:
            logger.error(f"❌ AI forecast generation failed: {str(e)}")


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
