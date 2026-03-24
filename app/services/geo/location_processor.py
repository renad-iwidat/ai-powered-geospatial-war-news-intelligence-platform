"""
=============================================================================
Location Processing Service (Hardcoded Locations)
=============================================================================
يقرأ أخبار عربية، يستخرج أسماء أماكن من قائمة محددة مسبقاً (hardcoded).

الخطوات:
1. قراءة أخبار عربية (ترجمة أو أصل عربي)
2. استخراج أسماء أماكن باستخدام NER
3. البحث عن الأماكن المستخرجة في قائمة المواقع المعرّفة
4. خزن الأحداث مع المواقع المرتبطة
=============================================================================
"""

import asyncio
import asyncpg
import re
from typing import Dict, Optional, List

from ..nlp.ner_simple import extract_places_simple


# ============================================================================
# Configuration
# ============================================================================
# حروف جر عربية قد تكون ملتصقة بأسماء الأماكن
_AR_PREFIXES = ("و", "ف", "ب", "ك", "ل")

# ============================================================================
# قائمة المدن والدول الأساسية (Hardcoded)
# ============================================================================
# هذه القائمة تحتوي على المدن والدول المهمة مع إحداثياتها الصحيحة
# لا نعتمد على قاعدة البيانات للمواقع، كل شيء معرّف هنا
LOCATIONS_DATABASE = {
    # الدول
    'لبنان': {'country_code': 'LB', 'lat': 33.8547, 'lng': 35.8623, 'type': 'country'},
    'سوريا': {'country_code': 'SY', 'lat': 34.8021, 'lng': 38.9968, 'type': 'country'},
    'فلسطين': {'country_code': 'PS', 'lat': 31.9454, 'lng': 35.2338, 'type': 'country'},
    'العراق': {'country_code': 'IQ', 'lat': 33.2232, 'lng': 43.6793, 'type': 'country'},
    'إيران': {'country_code': 'IR', 'lat': 32.4279, 'lng': 53.6880, 'type': 'country'},
    'السعودية': {'country_code': 'SA', 'lat': 23.8859, 'lng': 45.0792, 'type': 'country'},
    'الإمارات': {'country_code': 'AE', 'lat': 23.4241, 'lng': 53.8478, 'type': 'country'},
    'مصر': {'country_code': 'EG', 'lat': 26.8206, 'lng': 30.8025, 'type': 'country'},
    'الأردن': {'country_code': 'JO', 'lat': 30.5852, 'lng': 36.2384, 'type': 'country'},
    'تونس': {'country_code': 'TN', 'lat': 33.8869, 'lng': 9.5375, 'type': 'country'},
    'المغرب': {'country_code': 'MA', 'lat': 31.7917, 'lng': -7.0926, 'type': 'country'},
    'الجزائر': {'country_code': 'DZ', 'lat': 28.0339, 'lng': 1.6596, 'type': 'country'},
    'ليبيا': {'country_code': 'LY', 'lat': 26.3351, 'lng': 17.2283, 'type': 'country'},
    'اليمن': {'country_code': 'YE', 'lat': 15.3694, 'lng': 48.5150, 'type': 'country'},
    'عمان': {'country_code': 'OM', 'lat': 21.4735, 'lng': 55.9754, 'type': 'country'},
    'الكويت': {'country_code': 'KW', 'lat': 29.3117, 'lng': 47.4818, 'type': 'country'},
    'قطر': {'country_code': 'QA', 'lat': 25.3548, 'lng': 51.1839, 'type': 'country'},
    'البحرين': {'country_code': 'BH', 'lat': 26.0667, 'lng': 50.5577, 'type': 'country'},
    'إسرائيل': {'country_code': 'IL', 'lat': 31.0461, 'lng': 34.8516, 'type': 'country'},
    'تركيا': {'country_code': 'TR', 'lat': 38.9637, 'lng': 35.2433, 'type': 'country'},
    'اليونان': {'country_code': 'GR', 'lat': 39.0742, 'lng': 21.8243, 'type': 'country'},
    'فرنسا': {'country_code': 'FR', 'lat': 46.2276, 'lng': 2.2137, 'type': 'country'},
    'بريطانيا': {'country_code': 'GB', 'lat': 55.3781, 'lng': -3.4360, 'type': 'country'},
    'أمريكا': {'country_code': 'US', 'lat': 37.0902, 'lng': -95.7129, 'type': 'country'},
    'روسيا': {'country_code': 'RU', 'lat': 61.5240, 'lng': 105.3188, 'type': 'country'},
    'الهند': {'country_code': 'IN', 'lat': 20.5937, 'lng': 78.9629, 'type': 'country'},
    'الصين': {'country_code': 'CN', 'lat': 35.8617, 'lng': 104.1954, 'type': 'country'},
    'اليابان': {'country_code': 'JP', 'lat': 36.2048, 'lng': 138.2529, 'type': 'country'},
    
    # العواصم والمدن المهمة
    'بيروت': {'country_code': 'LB', 'lat': 33.8886, 'lng': 35.4955, 'type': 'city'},
    'دمشق': {'country_code': 'SY', 'lat': 33.5138, 'lng': 36.2765, 'type': 'city'},
    'عمّان': {'country_code': 'JO', 'lat': 31.9539, 'lng': 35.9106, 'type': 'city'},
    'بغداد': {'country_code': 'IQ', 'lat': 33.3128, 'lng': 44.3615, 'type': 'city'},
    'طهران': {'country_code': 'IR', 'lat': 35.6892, 'lng': 51.3890, 'type': 'city'},
    'الرياض': {'country_code': 'SA', 'lat': 24.7136, 'lng': 46.6753, 'type': 'city'},
    'دبي': {'country_code': 'AE', 'lat': 25.2048, 'lng': 55.2708, 'type': 'city'},
    'القاهرة': {'country_code': 'EG', 'lat': 30.0444, 'lng': 31.2357, 'type': 'city'},
    'تونس': {'country_code': 'TN', 'lat': 36.8065, 'lng': 10.1686, 'type': 'city'},
    'الجزائر': {'country_code': 'DZ', 'lat': 36.7538, 'lng': 3.0588, 'type': 'city'},
    'طرابلس': {'country_code': 'LY', 'lat': 32.8872, 'lng': 13.1913, 'type': 'city'},
    'صنعاء': {'country_code': 'YE', 'lat': 15.3694, 'lng': 48.5150, 'type': 'city'},
    'مسقط': {'country_code': 'OM', 'lat': 23.6100, 'lng': 58.5400, 'type': 'city'},
    'الكويت': {'country_code': 'KW', 'lat': 29.3759, 'lng': 47.9774, 'type': 'city'},
    'الدوحة': {'country_code': 'QA', 'lat': 25.2854, 'lng': 51.5310, 'type': 'city'},
    'المنامة': {'country_code': 'BH', 'lat': 26.2167, 'lng': 50.5833, 'type': 'city'},
    'القدس': {'country_code': 'PS', 'lat': 31.7683, 'lng': 35.2137, 'type': 'city'},
    'غزة': {'country_code': 'PS', 'lat': 31.5017, 'lng': 34.4668, 'type': 'city'},
    'إسطنبول': {'country_code': 'TR', 'lat': 41.0082, 'lng': 28.9784, 'type': 'city'},
    'أنقرة': {'country_code': 'TR', 'lat': 39.9334, 'lng': 32.8597, 'type': 'city'},
    'باريس': {'country_code': 'FR', 'lat': 48.8566, 'lng': 2.3522, 'type': 'city'},
    'لندن': {'country_code': 'GB', 'lat': 51.5074, 'lng': -0.1278, 'type': 'city'},
    'نيويورك': {'country_code': 'US', 'lat': 40.7128, 'lng': -74.0060, 'type': 'city'},
    'موسكو': {'country_code': 'RU', 'lat': 55.7558, 'lng': 37.6173, 'type': 'city'},
    'دلهي': {'country_code': 'IN', 'lat': 28.7041, 'lng': 77.1025, 'type': 'city'},
    'بكين': {'country_code': 'CN', 'lat': 39.9042, 'lng': 116.4074, 'type': 'city'},
    'طوكيو': {'country_code': 'JP', 'lat': 35.6762, 'lng': 139.6503, 'type': 'city'},
}


# ============================================================================
# Helper Functions
# ============================================================================

async def _get_ar_language_id(conn: asyncpg.Connection) -> int:
    """
    الحصول على ID اللغة العربية من قاعدة البيانات.
    
    Raises:
        RuntimeError: إذا لم توجد اللغة العربية
    """
    import logging
    try:
        row = await conn.fetchrow("SELECT id FROM languages WHERE code='ar' LIMIT 1;")
        if not row:
            logging.warning("Arabic language row not found in languages table (code='ar'). Attempting to create it...")
            # Try to insert Arabic language
            await conn.execute(
                "INSERT INTO languages (code, name) VALUES ('ar', 'Arabic') ON CONFLICT (code) DO NOTHING"
            )
            row = await conn.fetchrow("SELECT id FROM languages WHERE code='ar' LIMIT 1;")
            if not row:
                raise RuntimeError("Failed to create or find Arabic language in database")
        return int(row["id"])
    except Exception as e:
        logging.error(f"Error getting Arabic language ID: {str(e)}", exc_info=True)
        raise


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
    - ودمشق -> دمشق (فصل الواو)
    
    لكن لا يفصل من كلمات قصيرة جداً:
    - لو (2 أحرف) -> لو (بدون فصل)
    - بك (2 أحرف) -> بك (بدون فصل)
    """
    token = (token or "").strip()

    # كلمات قصيرة جداً: لا تفصل
    if len(token) < 4:
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
    
    استبعاد المصادر 17 و 18 (مصادر النهار)
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
          AND rn.source_id NOT IN (17, 18)
        ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC NULLS LAST
        LIMIT $2
        """,
        ar_id,
        batch_size
    )


def find_locations_in_text(text: str) -> List[tuple]:
    """
    البحث عن المواقع المعرّفة في النص باستخدام Regex.
    
    يبحث عن أسماء المواقع من LOCATIONS_DATABASE في النص.
    يتعامل مع:
    - حروف الجر الملتصقة (و، ف، ب، ك، ل)
    - الرموز الإضافية (فاصلات، نقاط، نقطتان)
    - المسافات الإضافية
    
    Returns:
        قائمة من (location_name, location_data) للمواقع المكتشفة
    """
    found_locations = []
    seen = set()
    
    # بناء regex pattern لكل موقع
    for location_name in LOCATIONS_DATABASE.keys():
        # Escape special regex characters
        escaped_name = re.escape(location_name)
        
        # Pattern يتعامل مع:
        # 1. حروف جر قبل الاسم: [وفبكل]?
        # 2. الاسم نفسه
        # 3. رموز بعد الاسم: [،:\.]*
        # 4. كلمات حدود: \b
        pattern = rf'\b[وفبكل]?{escaped_name}[،:\.]*\b'
        
        # البحث عن جميع التطابقات
        matches = re.finditer(pattern, text)
        
        for match in matches:
            if location_name not in seen:
                found_locations.append((location_name, LOCATIONS_DATABASE[location_name]))
                seen.add(location_name)
    
    return found_locations


# ============================================================================
# Main Processing Function
# ============================================================================

async def process_locations(
    pool: asyncpg.Pool,
    batch_size: int = 20
) -> Dict:
    """
    معالجة الأماكن في الأخبار.
    
    الخطوات:
    1. قراءة أخبار عربية (ترجمة أو raw عربي)
    2. استخراج أسماء أماكن من النص
    3. البحث عن الأماكن في قائمة LOCATIONS_DATABASE
    4. خزن الأحداث مع المواقع المرتبطة
    
    Args:
        pool: connection pool لقاعدة البيانات
        batch_size: عدد الأخبار المراد معالجتها
    
    Returns:
        dict يحتوي على إحصائيات:
        - processed_news: عدد الأخبار المقروءة
        - locations_found: عدد المواقع المكتشفة
        - events_created: عدد الروابط المنشأة
    """
    import logging
    
    # ============================================================================
    # Step 1: Fetch News Batch
    # ============================================================================
    try:
        async with pool.acquire() as conn:
            news_rows = await _get_news_batch(conn, batch_size)
    except Exception as e:
        logging.error(f"Error fetching news batch: {str(e)}", exc_info=True)
        return {
            "processed_news": 0,
            "locations_found": 0,
            "events_created": 0
        }

    processed_news = 0
    locations_found = 0
    events_created = 0
    locations_by_country = {}
    
    logging.info(f"📍 Processing {len(news_rows)} news articles for location extraction")

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
        # Step 3: Find Locations in Text
        # ============================================================================
        try:
            found_locs = find_locations_in_text(text)
        except Exception as e:
            logging.error(f"  ✗ Error finding locations in news {raw_news_id}: {str(e)}", exc_info=True)
            found_locs = []
        
        if not found_locs:
            continue

        # ============================================================================
        # Step 4: Store Events for Each Location
        # ============================================================================
        async with pool.acquire() as conn:
            for place_name, loc_data in found_locs:
                locations_found += 1
                country_code = loc_data['country_code']
                
                # Track locations by country
                if country_code not in locations_by_country:
                    locations_by_country[country_code] = []
                locations_by_country[country_code].append(place_name)
                
                try:
                    # إدراج أو تحديث المكان في قاعدة البيانات
                    row = await conn.fetchrow(
                        """
                        INSERT INTO locations (name, country_code, latitude, longitude, region_level, osm_id, osm_type)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (name, country_code)
                        DO UPDATE SET
                          latitude = EXCLUDED.latitude,
                          longitude = EXCLUDED.longitude
                        RETURNING id
                        """,
                        place_name,
                        loc_data['country_code'],
                        loc_data['lat'],
                        loc_data['lng'],
                        loc_data['type'],
                        hash(place_name) % 2147483647,  # Simple hash for osm_id
                        'hardcoded'
                    )
                    
                    location_id = int(row["id"])
                    
                    # إنشاء ربط بين الخبر والمكان
                    await conn.execute(
                        """
                        INSERT INTO news_events (raw_news_id, location_id, place_name, event_type)
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (raw_news_id, location_id) DO NOTHING
                        """,
                        raw_news_id,
                        location_id,
                        place_name,
                        "location_mention"
                    )
                    events_created += 1
                    
                except Exception as e:
                    logging.error(f"  ✗ Error storing location {place_name} for news {raw_news_id}: {str(e)}", exc_info=True)
                    continue

    # ============================================================================
    # Log Summary
    # ============================================================================
    logging.info(f"✅ Location extraction completed:")
    logging.info(f"  • News articles processed: {processed_news}")
    logging.info(f"  • Locations detected: {locations_found}")
    logging.info(f"  • Events created: {events_created}")
    
    if locations_by_country:
        logging.info(f"  • Breakdown by country:")
        for country_code in sorted(locations_by_country.keys()):
            unique_locs = list(set(locations_by_country[country_code]))
            logging.info(f"    - {country_code}: {len(unique_locs)} unique locations ({', '.join(unique_locs[:3])}{'...' if len(unique_locs) > 3 else ''})")

    # ============================================================================
    # Return Statistics
    # ============================================================================
    return {
        "processed_news": processed_news,
        "places_detected": locations_found,
        "locations_upserted": locations_found,
        "events_created": events_created
    }
