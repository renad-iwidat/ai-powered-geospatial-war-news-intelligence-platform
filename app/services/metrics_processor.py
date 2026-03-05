"""
=============================================================================
Metrics Processing Service
=============================================================================
يقرأ الأخبار من قاعدة البيانات ويستخرج metrics منها ويخزنها.

الخطوات:
1. قراءة أخبار عربية (ترجمة أو أصل عربي)
2. استخراج metrics باستخدام extract_war_metrics
3. خزن metrics في جدول event_metrics مع snippet من النص
=============================================================================
"""

import asyncpg
from typing import Dict, Optional, Tuple
from .metrics_extractor import extract_war_metrics


# ============================================================================
# Helper Functions
# ============================================================================

async def _get_lang_id(conn: asyncpg.Connection, code: str) -> int:
    """
    الحصول على ID اللغة من جدول languages.
    
    Args:
        conn: اتصال قاعدة البيانات
        code: كود اللغة (مثل 'ar', 'en')
    
    Returns:
        ID اللغة
    
    Raises:
        RuntimeError: إذا لم توجد اللغة
    """
    row = await conn.fetchrow("SELECT id FROM languages WHERE code=$1 LIMIT 1;", code)
    if not row:
        raise RuntimeError(f"Language code '{code}' not found in languages table.")
    return int(row["id"])


async def _pick_text_for_news(
    conn: asyncpg.Connection,
    raw_news_id: int,
    rn_lang_code: str,
    title_original: Optional[str],
    content_original: Optional[str],
    ar_lang_id: int
) -> Tuple[str, str]:
    """
    اختيار النص المناسب للمعالجة.
    
    الأولوية:
    1. إذا الخبر عربي أصلاً: استخدم الأصل
    2. إذا غير عربي: جرّب ترجمة عربية
    3. إذا ما في ترجمة: استخدم الأصل (قد يكون إنجليزي)
    
    Returns:
        (text_to_use, prefer_lang)
        prefer_lang: 'ar' إذا النص عربي، 'en' إذا الأصل غير عربي
    """
    # إذا الخبر عربي: خذ الأصل
    if rn_lang_code == "ar":
        text = (title_original or "") + "\n" + (content_original or "")
        return text.strip(), "ar"

    # غير عربي: جرّب ترجمة عربية
    t = await conn.fetchrow(
        """
        SELECT title, content
        FROM translations
        WHERE raw_news_id=$1 AND language_id=$2
        ORDER BY id DESC
        LIMIT 1
        """,
        raw_news_id, ar_lang_id
    )

    if t and ((t["title"] or "").strip() or (t["content"] or "").strip()):
        text = (t["title"] or "") + "\n" + (t["content"] or "")
        return text.strip(), "ar"

    # ما في ترجمة عربية: ارجع للأصل
    text = (title_original or "") + "\n" + (content_original or "")
    return text.strip(), "en"


async def _get_anchor_event_id(conn: asyncpg.Connection, raw_news_id: int) -> Optional[int]:
    """
    الحصول على أول event_id للخبر.
    
    نستخدم أول event كـ anchor لخزن جميع metrics الخبر.
    """
    row = await conn.fetchrow(
        "SELECT id FROM news_events WHERE raw_news_id=$1 ORDER BY id ASC LIMIT 1;",
        raw_news_id
    )
    return int(row["id"]) if row else None


# ============================================================================
# Main Processing Function
# ============================================================================

async def process_metrics(pool: asyncpg.Pool, batch_size: int = 50) -> Dict:
    """
    معالجة metrics للأخبار.
    
    يقرأ أخبار:
    - فيها أرقام (has_numbers = true)
    - لها events (حتى نقدر نخزن metrics على event_id)
    - لم تتم معالجتها سابقاً (ما في metrics لها)
    
    ثم يستخرج metrics ويخزنها في جدول event_metrics.
    
    Args:
        pool: connection pool لقاعدة البيانات
        batch_size: عدد الأخبار المراد معالجتها في كل دفعة
    
    Returns:
        dict يحتوي على إحصائيات المعالجة:
        - processed_news: عدد الأخبار المقروءة
        - metrics_created: عدد metrics المخزنة
        - skipped_no_text: أخبار بدون نص
        - skipped_no_metrics: أخبار بدون metrics
    """
    
    # ============================================================================
    # Step 1: Get Language ID
    # ============================================================================
    async with pool.acquire() as conn:
        ar_lang_id = await _get_lang_id(conn, "ar")

        # ============================================================================
        # Step 2: Fetch News Batch
        # ============================================================================
        # جيب أخبار فيها أرقام ولسا ما أخذت metrics
        rows = await conn.fetch(
            """
            SELECT
              rn.id AS raw_news_id,
              rn.title_original,
              rn.content_original,
              l.code AS rn_lang_code
            FROM raw_news rn
            JOIN languages l ON l.id = rn.language_id
            WHERE rn.has_numbers = true
              AND EXISTS (SELECT 1 FROM news_events ne WHERE ne.raw_news_id = rn.id)
              AND NOT EXISTS (
                SELECT 1
                FROM news_events ne
                JOIN event_metrics em ON em.event_id = ne.id
                WHERE ne.raw_news_id = rn.id
              )
            ORDER BY rn.id DESC
            LIMIT $1
            """,
            batch_size
        )

    # ============================================================================
    # Step 3: Process Each News Item
    # ============================================================================
    processed_news = 0
    metrics_created = 0
    skipped_no_text = 0
    skipped_no_metrics = 0

    for r in rows:
        processed_news += 1
        raw_news_id = int(r["raw_news_id"])

        # اختيار النص المناسب
        async with pool.acquire() as conn:
            event_id = await _get_anchor_event_id(conn, raw_news_id)
            if not event_id:
                continue

            text, prefer_lang = await _pick_text_for_news(
                conn,
                raw_news_id=raw_news_id,
                rn_lang_code=r["rn_lang_code"],
                title_original=r["title_original"],
                content_original=r["content_original"],
                ar_lang_id=ar_lang_id
            )

        # تخطي إذا ما في نص
        if not text:
            skipped_no_text += 1
            continue

        # استخراج metrics
        metrics = extract_war_metrics(text, prefer_lang=prefer_lang)
        if not metrics:
            skipped_no_metrics += 1
            continue

        # ============================================================================
        # Step 4: Store Metrics in Database
        # ============================================================================
        async with pool.acquire() as conn:
            for m in metrics:
                # خزن الـ metric مع snippet من النص (أول 200 حرف)
                await conn.execute(
                    """
                    INSERT INTO event_metrics (event_id, metric_type, value, snippet)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT DO NOTHING
                    """,
                    event_id,
                    m["metric_type"],
                    m["value"],
                    m["snippet"]
                )
                metrics_created += 1

    # ============================================================================
    # Return Statistics
    # ============================================================================
    return {
        "processed_news": processed_news,
        "metrics_created": metrics_created,
        "skipped_no_text": skipped_no_text,
        "skipped_no_metrics": skipped_no_metrics
    }
