#!/usr/bin/env python3
"""
Standalone Scheduler Runner
Run background tasks independently from the FastAPI server
Useful for deployment scenarios where you want separate scheduler process
"""

import sys
import os
import logging
import signal
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.scheduler import SchedulerManager
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler_manager = None


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    global scheduler_manager
    logger.info("\n📛 Received shutdown signal, stopping scheduler...")
    if scheduler_manager:
        scheduler_manager.stop()
    sys.exit(0)


def main():
    """Main entry point for standalone scheduler"""
    global scheduler_manager
    
    # Load .env if present so local runs pick up API_BASE_URL
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=False)
    except Exception:
        pass

    # Get API base URL from environment or use default
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:7235")
    
    logger.info("=" * 60)
    logger.info("🚀 GeoNews AI - Background Task Scheduler")
    logger.info("=" * 60)
    logger.info(f"API Base URL: {api_base_url}")
    logger.info("")
    
    # Create and start scheduler
    scheduler_manager = SchedulerManager(api_base_url=api_base_url)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        scheduler_manager.start()
        logger.info("")
        logger.info("✅ Scheduler is running. Press Ctrl+C to stop.")
        logger.info("")
        
        # Keep the scheduler running
        import time
        while True:
            time.sleep(1)
    
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
