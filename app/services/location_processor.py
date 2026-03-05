"""
=============================================================================
Location Processing Service
=============================================================================
يقرأ أخبار عربية، يستخرج أسماء أماكن، يحول إلى إحداثيات، ويخزن في قاعدة البيانات.

الخطوات:
1. قراءة أخبار عربية (ترجمة أو أصل عربي)
2. استخراج أسماء أماكن باستخدام NER
3. تحويل الأسماء إلى إحداثيات باستخدام Nominatim
4. خزن الأماكن والربط مع الأخبار
=============================================================================
"""

import asyncio
import asyncpg
import httpx
import re
from typing import Dict, Optional

from .ner_ar import extract_places_ner
from .geocode_osm import geocode_nominatim


# ============================================================================
# Configuration
# ============================================================================
# User-Agent للـ Nominatim API (مهم جداً)
# يفضل أن يكون فيه بيانات تواصل حقيقية
USER_AGENT = "GeoNewsAI/1.0 (contact: lmaaljohare@gmail.com)"

# حروف جر عربية قد تكون ملتصقة بأسماء الأماكن
_AR_PREFIXES = ("و", "ف", "ب", "ك", "ل")


# ============================================================================
# Helper Functions
# ============================================================================

async def _get_ar_language_id(conn: asyncpg.Connection) -> int:
    """
    الحصول على ID اللغة العربية من قاعدة البيانات.
    
    Raises:
        RuntimeError: إذا لم توجد اللغة العربية
    """
    row = await conn.fetchrow("SELECT id FROM languages WHERE code='ar' LIMIT 1;")
    if not row:
        raise RuntimeError("Arabic language row not found in languages table (code='ar').")
    return int(row["id"])


def preprocess_text_for_ner(text: str) -> str:
    """
    تحضير النص قبل معالجة NER.
    
    يفصل حروف الجر عن أسماء الأماكن:
    - بالامارات -> ب الامارات
    - والبحرين -> و البحرين
    
    هذا يساعد NER على التعرف على الأماكن بشكل أفضل.
    """
    if not text:
        return text

    # فصل حرف جر واحد قبل "ال"
    text = re.sub(r"\b([وفبكل])(?=ال)", r"\1 ", text)

    return text


def split_prefix_if_safe(token: str) -> str:
    """
    فصل حرف جر واحد من بداية الكلمة إذا كان آمن.
    
    أمثلة:
    - لايران -> ايران (فصل اللام)
    - باسرائيل -> اسرائيل (فصل الباء)
    
    لكن لا يفصل من كلمات قصيرة:
    - لبنان (6 أحرف) -> لبنان (بدون فصل)
    - لندن (4 أحرف) -> لندن (بدون فصل)
    """
    token = (token or "").strip()

    # كلمات قصيرة: لا تفصل
    if len(token) < 6:
        return token

    # فصل حرف جر واحد من البداية
    if token[0] in _AR_PREFIXES:
        return token[1:].strip()

    return token


async def _get_news_batch(conn: asyncpg.Connection, batch_size: int) -> list:
    """
    قراءة دفعة من الأخبار العربية التي لم تتم معالجتها بعد.
    
    يجيب نص عربي من مصدرين:
    1. ترجمة عربية من جدول translations
    2. أو raw_news إذا كان أصلاً عربي
    
    يجيب فقط الأخبار اللي لسا ما إلها events.
    """
    ar_id = await _get_ar_language_id(conn)

    return await conn.fetch(
        """
        SELECT
          rn.id AS raw_news_id,
          COALESCE(t.title, rn.title_original)      AS title_ar,
          COALESCE(t.content, rn.content_original)  AS content_ar
        FROM raw_news rn
        LEFT JOIN translations t
          ON t.raw_news_id = rn.id AND t.language_id = $1
        WHERE
          (t.id IS NOT NULL OR rn.language_id = $1)
          AND NOT EXISTS (
            SELECT 1 FROM news_events ne WHERE ne.raw_news_id = rn.id
          )
        ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC NULLS LAST
        LIMIT $2
        """,
        ar_id,
        batch_size
    )


async def _find_cached_location(conn: asyncpg.Connection, name: str) -> Optional[int]:
    """
    البحث عن مكان في الـ cache (جدول locations).
    
    إذا الاسم موجود، رجّع ID.
    (لاحقًا ممكن نعملها أدق حسب (name, country_code))
    """
    row = await conn.fetchrow(
        "SELECT id FROM locations WHERE name=$1 LIMIT 1;",
        name
    )
    return int(row["id"]) if row else None


async def _upsert_location(
    conn: asyncpg.Connection,
    name: str,
    country_code: str,
    lat: float,
    lng: float,
    osm_id: int,
    osm_type: str
) -> int:
    """
    إدراج أو تحديث مكان في قاعدة البيانات.
    
    يستخدم (osm_type, osm_id) كـ unique key.
    إذا كان المكان موجود، يحدّث الإحداثيات والبيانات.
    """
    row = await conn.fetchrow(
        """
        INSERT INTO locations (name, country_code, latitude, longitude, region_level, osm_id, osm_type)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (osm_type, osm_id)
        DO UPDATE SET
          latitude = EXCLUDED.latitude,
          longitude = EXCLUDED.longitude,
          country_code = EXCLUDED.country_code,
          name = EXCLUDED.name
        RETURNING id
        """,
        name,
        country_code,
        lat,
        lng,
        "unknown",
        osm_id,
        osm_type
    )
    return int(row["id"])


async def geocode_best_effort(
    client: httpx.AsyncClient,
    place: str,
    sleep_seconds: float
) -> tuple:
    """
    محاولة تحويل اسم مكان إلى إحداثيات.
    
    الخطوات:
    1. جرّب البحث عن الاسم الأصلي
    2. إذا ما طلع: جرّب بعد فصل حرف جر
    
    Returns:
        (geo_dict, place_name_used) أو (None, None) إذا فشل
    """
    # محاولة أولى
    geo = await geocode_nominatim(client, place)
    await asyncio.sleep(sleep_seconds)

    if geo and geo.get("country_code") and geo.get("osm_id") and geo.get("osm_type"):
        return geo, place

    # محاولة ثانية بعد فصل prefix
    place2 = split_prefix_if_safe(place)

    if place2 != place:
        geo2 = await geocode_nominatim(client, place2)
        await asyncio.sleep(sleep_seconds)

        if geo2 and geo2.get("country_code") and geo2.get("osm_id") and geo2.get("osm_type"):
            return geo2, place2

    return None, None


async def _insert_event(
    conn: asyncpg.Connection,
    raw_news_id: int,
    location_id: int,
    place_name: str
) -> None:
    """
    إنشاء ربط بين خبر ومكان (news_event).
    
    يستخدم ON CONFLICT لتجنب التكرار.
    """
    await conn.execute(
        """
        INSERT INTO news_events (raw_news_id, location_id, place_name, event_type)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (raw_news_id, location_id) DO NOTHING
        """,
        raw_news_id,
        location_id,
        place_name,
        "unknown"
    )


# ============================================================================
# Main Processing Function
# ============================================================================

async def process_locations(
    pool: asyncpg.Pool,
    batch_size: int = 20,
    sleep_seconds: float = 1.0
) -> Dict:
    """
    معالجة الأماكن في الأخبار.
    
    الخطوات:
    1. قراءة أخبار عربية (ترجمة أو raw عربي)
    2. استخراج أسماء أماكن باستخدام NER
    3. تحويل الأسماء إلى إحداثيات (Nominatim)
    4. خزن الأماكن في جدول locations
    5. ربط الأخبار بالأماكن في جدول news_events
    
    Args:
        pool: connection pool لقاعدة البيانات
        batch_size: عدد الأخبار المراد معالجتها
        sleep_seconds: تأخير بين طلبات Nominatim (rate limiting)
    
    Returns:
        dict يحتوي على إحصائيات:
        - processed_news: عدد الأخبار المقروءة
        - places_detected: عدد الأماكن المستخرجة
        - locations_upserted: عدد الأماكن المخزنة
        - events_created: عدد الروابط المنشأة
    """
    
    # ============================================================================
    # Step 1: Fetch News Batch
    # ============================================================================
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as client:
        async with pool.acquire() as conn:
            news_rows = await _get_news_batch(conn, batch_size)

        processed_news = 0
        places_detected = 0
        locations_upserted = 0
        events_created = 0

        # ============================================================================
        # Step 2: Process Each News Item
        # ============================================================================
        for n in news_rows:
            processed_news += 1
            raw_news_id = int(n["raw_news_id"])
            
            # دمج العنوان والمحتوى
            text = (n["title_ar"] or "") + "\n" + (n["content_ar"] or "")

            # تحضير النص لـ NER
            text = preprocess_text_for_ner(text)

            # ============================================================================
            # Step 3: Extract Places Using NER
            # ============================================================================
            places = extract_places_ner(text)
            if not places:
                continue

            # حد أعلى لكل خبر لتقليل geocode requests
            for place in places[:3]:
                places_detected += 1

                # ============================================================================
                # Step 4: Geocode Place Name
                # ============================================================================
                geo, place_clean = await geocode_best_effort(client, place, sleep_seconds)

                if not geo:
                    continue
                if not geo.get("osm_id") or not geo.get("osm_type"):
                    continue

                # ============================================================================
                # Step 5: Store Location and Create Event
                # ============================================================================
                async with pool.acquire() as conn:
                    loc_id = await _upsert_location(
                        conn,
                        place_clean,
                        geo["country_code"],
                        geo["lat"],
                        geo["lng"],
                        geo["osm_id"],
                        geo["osm_type"],
                    )
                    locations_upserted += 1

                    await _insert_event(conn, raw_news_id, loc_id, place)
                    events_created += 1

        # ============================================================================
        # Return Statistics
        # ============================================================================
        return {
            "processed_news": processed_news,
            "places_detected": places_detected,
            "locations_upserted": locations_upserted,
            "events_created": events_created
        }
