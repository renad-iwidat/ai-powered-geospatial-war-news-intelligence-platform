"""Location Processing Service (Database-driven)
----------------------------------------------
The service matches Arabic news articles against the curated entries in the
`locations` table and strictly avoids restricted daytime sources.
"""

import logging
import re
from typing import Dict, List, Pattern

import asyncpg

from ..nlp.ner_simple import normalize_ar

logger = logging.getLogger(__name__)

_RESTRICTED_SOURCE_IDS = (17, 18)


def preprocess_text_for_ner(text: str) -> str:
    return text or ""


def _compile_location_pattern(normalized_name: str) -> Pattern:
    prefix_pattern = r"(?:[وفبكل]?ال)?"
    suffix_pattern = r"(?:يّ|ي|ية|يات|يون|يان|ان|ين|ة)?"
    return re.compile(
        rf"(?<!\w){prefix_pattern}{re.escape(normalized_name)}{suffix_pattern}(?!\w)",
        re.IGNORECASE,
    )


def find_locations_in_text(text: str, candidates: List[Dict]) -> List[Dict]:
    if not text or not candidates:
        return []
    normalized_text = normalize_ar(text)
    matches: List[Dict] = []
    seen_ids = set()
    for candidate in candidates:
        cid = candidate["id"]
        if cid in seen_ids:
            continue
        if candidate["pattern"].search(normalized_text):
            matches.append(candidate)
            seen_ids.add(cid)
    return matches


async def _get_ar_language_id(conn: asyncpg.Connection) -> int:
    import logging as _logging
    try:
        row = await conn.fetchrow("SELECT id FROM languages WHERE code='ar' LIMIT 1;")
        if not row:
            _logging.warning("Arabic language row missing; creating placeholder...")
            await conn.execute(
                "INSERT INTO languages (code, name) VALUES ('ar', 'Arabic') ON CONFLICT (code) DO NOTHING"
            )
            row = await conn.fetchrow("SELECT id FROM languages WHERE code='ar' LIMIT 1;")
            if not row:
                raise RuntimeError("Failed to create or find the Arabic language row")
        return int(row["id"])
    except Exception as exc:
        _logging.error(f"Error getting Arabic language ID: {exc}", exc_info=True)
        raise


async def _load_location_candidates(pool: asyncpg.Pool) -> List[Dict]:
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, name, country_code, latitude, longitude, region_level, osm_id, osm_type
            FROM locations
            WHERE name IS NOT NULL AND LENGTH(TRIM(name)) > 0
            """
        )
    candidates: List[Dict] = []
    for row in rows:
        name = row["name"]
        normalized_name = normalize_ar(name)
        if not normalized_name:
            continue
        candidates.append({
            "id": row["id"],
            "name": name,
            "pattern": _compile_location_pattern(normalized_name),
            "country_code": row["country_code"] or "UNKNOWN",
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "region_level": row["region_level"],
            "osm_id": row["osm_id"],
            "osm_type": row["osm_type"],
        })
    return candidates


async def _get_news_batch(conn: asyncpg.Connection, batch_size: int) -> list:
    ar_id = await _get_ar_language_id(conn)
    return await conn.fetch(
        """
        SELECT
          rn.id AS raw_news_id,
          rn.source_id,
          COALESCE(t.title, rn.title_original) AS title_ar,
          COALESCE(t.content, rn.content_original) AS content_ar
        FROM raw_news rn
        LEFT JOIN translations t
          ON t.raw_news_id = rn.id AND t.language_id = $1
        WHERE
          (t.id IS NOT NULL OR rn.language_id = $1)
          AND NOT EXISTS (
            SELECT 1 FROM news_events ne WHERE ne.raw_news_id = rn.id
          )
          AND rn.source_id NOT IN (17, 18)
        ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC NULLS LAST
        LIMIT $2
        """,
        ar_id,
        batch_size,
    )


async def process_locations(pool: asyncpg.Pool, batch_size: int = 20) -> Dict:
    location_candidates = await _load_location_candidates(pool)
    if not location_candidates:
        logger.warning("Locations table is empty; extraction will not create events")
    try:
        async with pool.acquire() as conn:
            news_rows = await _get_news_batch(conn, batch_size)
    except Exception as exc:
        logger.error(f"Error fetching news batch: {exc}", exc_info=True)
        return {
            "processed_news": 0,
            "places_detected": 0,
            "locations_upserted": 0,
            "events_created": 0,
        }
    processed_news = 0
    locations_found = 0
    events_created = 0
    locations_by_country: Dict[str, List[str]] = {}
    logger.info(
        f"🔍 Processing {len(news_rows)} articles against {len(location_candidates)} database locations"
    )
    for n in news_rows:
        processed_news += 1
        raw_news_id = int(n["raw_news_id"])
        source_id = n["source_id"]
        if source_id in _RESTRICTED_SOURCE_IDS:
            continue
        text = (n["title_ar"] or "") + "\n" + (n["content_ar"] or "")
        text = preprocess_text_for_ner(text)
        found_locs = find_locations_in_text(text, location_candidates)
        if not found_locs:
            continue
        locations_found += len(found_locs)
        for loc in found_locs:
            country_code = loc.get("country_code", "UNKNOWN")
            locations_by_country.setdefault(country_code, []).append(loc["name"])
        try:
            async with pool.acquire() as conn:
                for loc in found_locs:
                    await conn.execute(
                        """
                        INSERT INTO news_events (raw_news_id, location_id, place_name, event_type)
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (raw_news_id, location_id) DO NOTHING
                        """,
                        raw_news_id,
                        loc["id"],
                        loc["name"],
                        "location_mention",
                    )
                    events_created += 1
        except Exception as exc:
            logger.error(f"  ✗ Error storing locations for news {raw_news_id}: {exc}", exc_info=True)
    logger.info("✅ Location extraction completed:")
    logger.info(f"  • Articles processed: {processed_news}")
    logger.info(f"  • Locations detected: {locations_found}")
    logger.info(f"  • Events created: {events_created}")
    if locations_by_country:
        logger.info("  • Breakdown by country:")
        for country_code in sorted(locations_by_country.keys()):
            unique_locs = list(set(locations_by_country[country_code]))
            logger.info(
                f"    - {country_code}: {len(unique_locs)} unique locations ({', '.join(unique_locs[:3])}{'...' if len(unique_locs) > 3 else ''})"
            )
    return {
        "processed_news": processed_news,
        "places_detected": locations_found,
        "locations_upserted": locations_found,
        "events_created": events_created,
    }
