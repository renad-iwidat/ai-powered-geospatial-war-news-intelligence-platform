#!/usr/bin/env python3
"""
Check processing status without triggering processing
"""

import asyncio
import httpx
import sys
from datetime import datetime

async def check_status():
    """Check processing status"""
    api_base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"📊 Checking processing status at {datetime.now().isoformat()}")
            
            response = await client.get(
                f"{api_base_url}/api/v1/data-processing/status"
            )
            response.raise_for_status()
            status = response.json()
            
            print("\n✅ Processing Status:")
            print(f"  Total Articles: {status['total_articles']}")
            print(f"  Articles with Events: {status['articles_with_events']}")
            print(f"  Articles without Events: {status['articles_without_events']}")
            print(f"  Total Events: {status['total_events']}")
            print(f"  Events with Metrics: {status['events_with_metrics']}")
            print(f"  Events without Metrics: {status['events_without_metrics']}")
            print(f"  Overall Completion: {status['processing_completion_percentage']}%")
            
            # Calculate what needs to be done
            print("\n📋 What needs processing:")
            if status['articles_without_events'] > 0:
                print(f"  - {status['articles_without_events']} articles need location extraction")
            if status['events_without_metrics'] > 0:
                print(f"  - {status['events_without_metrics']} events need metrics extraction")
            
            return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = asyncio.run(check_status())
    sys.exit(0 if success else 1)
