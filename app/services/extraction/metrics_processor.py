"""
Metrics Processing Service
Processes news articles to extract and store metrics in the database
"""

import re
import asyncpg
from .metrics_extractor import extract_metrics


# ============================================================================
# Main Processing Function
# ============================================================================

async def process_metrics(pool: asyncpg.Pool, batch_size: int = 20):
    """
    Process news articles to extract metrics and store them in database

    This function:
    1. Fetches unprocessed news articles that have content
    2. Extracts metrics (casualties, weapons, etc.) from the content
    3. Stores extracted metrics in the event_metrics table

    Args:
        pool: Database connection pool
        batch_size: Number of articles to process in one batch

    Returns:
        Dictionary with processing statistics:
        - processed_events: Number of articles processed
        - metrics_created: Total metrics extracted and stored
    """
    import logging
    logger = logging.getLogger(__name__)

    # ========================================================================
    # Fetch Unprocessed Articles with Content
    # ========================================================================
    logger.info(f"📊 Fetching events without metrics (batch size: {batch_size})...")

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    ne.id AS event_id,
                    ne.place_name,
                    vw.content_ar AS content
                FROM news_events ne
                JOIN vw_news_ar_feed vw ON vw.raw_news_id = ne.raw_news_id
                WHERE vw.has_numbers = true
                AND vw.content_ar IS NOT NULL 
                AND LENGTH(vw.content_ar) > 50
                AND NOT EXISTS (
                    SELECT 1
                    FROM event_metrics em
                    WHERE em.event_id = ne.id
                )
                LIMIT $1;
                """,
                batch_size,
            )
            logger.info(f"  ✓ Found {len(rows)} events to process")
    except Exception as e:
        logger.error(f"  ✗ Error fetching events for metrics processing: {str(e)}")
        return {
            "processed_events": 0,
            "metrics_created": 0,
        }

    processed = 0
    metrics_created = 0
    metrics_by_type = {}

    # ========================================================================
    # Process Each Article
    # ========================================================================
    logger.info(f"🔍 Processing {len(rows)} events for metrics extraction...")

    for r in rows:
        processed += 1

        event_id = r["event_id"]
        place_name = r["place_name"]
        text = r["content"] or ""

        # Extract metrics from the entire content
        try:
            metrics = extract_metrics(text)
        except Exception as e:
            logger.error(f"  ✗ Error extracting metrics from event {event_id} ({place_name}): {str(e)}")
            metrics = []

        if not metrics:
            continue

        # ================================================================
        # Store Metrics in Database
        # ================================================================

        async with pool.acquire() as conn:
            for m in metrics:
                # Store each metric with:
                # - event_id: Links metric to the news event
                # - metric_type: Type of metric (killed, missiles_launched, etc.)
                # - value: The numerical value
                # - snippet: First 200 chars of the snippet (for reference)
                
                try:
                    await conn.execute(
                        """
                        INSERT INTO event_metrics
                        (event_id, metric_type, value, snippet)
                        VALUES ($1,$2,$3,$4)
                        """,
                        event_id,
                        m["metric_type"],
                        m["value"],
                        m["snippet"][:200],
                    )
                    metrics_created += 1
                    
                    # Track metrics by type
                    metric_type = m["metric_type"]
                    metrics_by_type[metric_type] = metrics_by_type.get(metric_type, 0) + 1
                    
                except Exception as e:
                    logger.debug(f"  ⚠ Skipped metric for event {event_id}: {str(e)}")
                    pass

    # ========================================================================
    # Log Summary
    # ========================================================================
    logger.info(f"✅ Metrics extraction completed:")
    logger.info(f"  • Events processed: {processed}")
    logger.info(f"  • Metrics extracted: {metrics_created}")
    
    if metrics_by_type:
        logger.info(f"  • Breakdown by type:")
        for metric_type, count in sorted(metrics_by_type.items()):
            logger.info(f"    - {metric_type}: {count}")

    return {
        "processed_events": processed,
        "metrics_created": metrics_created,
    }


