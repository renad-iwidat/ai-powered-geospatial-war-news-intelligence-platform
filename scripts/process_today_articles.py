#!/usr/bin/env python3
"""
Process today's articles immediately
Extracts locations and metrics from unprocessed articles
"""

import asyncio
import httpx
import sys
from datetime import datetime

async def process_articles():
    """Process unprocessed articles"""
    api_base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            print(f"🔄 Starting data processing at {datetime.now().isoformat()}")
            
            # Extract locations
            print("  → Extracting locations from news articles...")
            response = await client.post(
                f"{api_base_url}/api/v1/data-processing/extract-locations",
                json={"batch_size": 100}
            )
            response.raise_for_status()
            location_result = response.json()
            print(f"  ✓ Locations extracted: {location_result.get('processed_count', 0)} articles processed")
            print(f"    - Events created: {location_result.get('events_created', 0)}")
            print(f"    - Locations found: {location_result.get('locations_found', 0)}")
            
            # Extract metrics
            print("  → Extracting metrics from events...")
            response = await client.post(
                f"{api_base_url}/api/v1/data-processing/extract-metrics",
                json={"batch_size": 200}
            )
            response.raise_for_status()
            metrics_result = response.json()
            print(f"  ✓ Metrics extracted: {metrics_result.get('processed_count', 0)} events processed")
            print(f"    - Metrics created: {metrics_result.get('metrics_created', 0)}")
            
            # Get status
            print("\n📊 Processing Status:")
            response = await client.get(
                f"{api_base_url}/api/v1/data-processing/status"
            )
            response.raise_for_status()
            status = response.json()
            print(f"  Total Articles: {status['total_articles']}")
            print(f"  Articles with Events: {status['articles_with_events']}")
            print(f"  Articles without Events: {status['articles_without_events']}")
            print(f"  Total Events: {status['total_events']}")
            print(f"  Events with Metrics: {status['events_with_metrics']}")
            print(f"  Events without Metrics: {status['events_without_metrics']}")
            print(f"  Overall Completion: {status['processing_completion_percentage']}%")
            
            print(f"\n✅ Data processing completed at {datetime.now().isoformat()}")
            return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = asyncio.run(process_articles())
    sys.exit(0 if success else 1)
