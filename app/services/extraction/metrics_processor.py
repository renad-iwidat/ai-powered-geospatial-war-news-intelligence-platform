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

    # ========================================================================
    # Fetch Unprocessed Articles with Content
    # ========================================================================

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                ne.id AS event_id,
                ne.place_name,
                COALESCE(t.content, rn.content_original) AS content
            FROM news_events ne
            JOIN raw_news rn ON rn.id = ne.raw_news_id
            LEFT JOIN translations t ON t.raw_news_id = rn.id
            WHERE rn.has_numbers = true
            AND (
                (t.content IS NOT NULL AND LENGTH(t.content) > 50)
                OR (rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 50)
            )
            AND NOT EXISTS (
                SELECT 1
                FROM event_metrics em
                WHERE em.event_id = ne.id
            )
            LIMIT $1;
            """,
            batch_size,
        )

    processed = 0
    metrics_created = 0

    # ========================================================================
    # Process Each Article
    # ========================================================================

    for r in rows:
        processed += 1

        event_id = r["event_id"]
        text = r["content"] or ""

        # Extract metrics from the entire content
        metrics = extract_metrics(text)

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
                except Exception:
                    # Skip duplicates or other errors
                    pass

    return {
        "processed_events": processed,
        "metrics_created": metrics_created,
    }


