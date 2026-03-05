"""
Verify that we're reading ALL content (Arabic + Translated)
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    print("=" * 80)
    print("VERIFICATION: What metrics_processor reads")
    print("=" * 80)
    
    # Exact same query as metrics_processor
    rows = await conn.fetch("""
        SELECT
            ne.id AS event_id,
            ne.place_name,
            l.code as original_language,
            COALESCE(t.content, rn.content_original) AS content,
            LENGTH(COALESCE(t.content, rn.content_original)) as content_len,
            CASE 
                WHEN t.content IS NOT NULL THEN 'FROM_TRANSLATION'
                ELSE 'FROM_ORIGINAL'
            END as source
        FROM news_events ne
        JOIN raw_news rn ON rn.id = ne.raw_news_id
        LEFT JOIN translations t ON t.raw_news_id = rn.id
        LEFT JOIN languages l ON l.id = rn.language_id
        WHERE (
            (t.content IS NOT NULL AND LENGTH(t.content) > 50)
            OR (rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 50)
        )
        ORDER BY ne.id DESC
        LIMIT 50
    """)
    
    # Count by language and source
    by_lang = {}
    by_source = {'FROM_TRANSLATION': 0, 'FROM_ORIGINAL': 0}
    
    for r in rows:
        lang = r['original_language']
        source = r['source']
        
        if lang not in by_lang:
            by_lang[lang] = {'FROM_TRANSLATION': 0, 'FROM_ORIGINAL': 0}
        
        by_lang[lang][source] += 1
        by_source[source] += 1
    
    print("\nLast 50 events by language and source:")
    for lang, counts in by_lang.items():
        total = counts['FROM_TRANSLATION'] + counts['FROM_ORIGINAL']
        print(f"\n{lang}: {total} events")
        print(f"  From translation: {counts['FROM_TRANSLATION']}")
        print(f"  From original: {counts['FROM_ORIGINAL']}")
    
    print(f"\nTotal: {by_source['FROM_TRANSLATION']} from translations, {by_source['FROM_ORIGINAL']} from original")
    
    # Check total available
    print("\n" + "=" * 80)
    print("TOTAL AVAILABLE FOR PROCESSING:")
    print("=" * 80)
    
    total = await conn.fetchrow("""
        SELECT
            COUNT(*) as total_events,
            COUNT(CASE WHEN l.code = 'ar' THEN 1 END) as arabic_events,
            COUNT(CASE WHEN l.code = 'en' THEN 1 END) as english_events,
            COUNT(CASE WHEN l.code = 'he' THEN 1 END) as hebrew_events
        FROM news_events ne
        JOIN raw_news rn ON rn.id = ne.raw_news_id
        LEFT JOIN translations t ON t.raw_news_id = rn.id
        LEFT JOIN languages l ON l.id = rn.language_id
        WHERE (
            (t.content IS NOT NULL AND LENGTH(t.content) > 50)
            OR (rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 50)
        )
    """)
    
    print(f"Total events with content: {total['total_events']}")
    print(f"  Arabic (original): {total['arabic_events']}")
    print(f"  English (translated): {total['english_events']}")
    print(f"  Hebrew (translated): {total['hebrew_events']}")
    
    # Sample from each language
    print("\n" + "=" * 80)
    print("SAMPLE FROM EACH LANGUAGE:")
    print("=" * 80)
    
    for lang_code in ['ar', 'en', 'he']:
        sample = await conn.fetchrow("""
            SELECT
                ne.id AS event_id,
                rn.title_original,
                COALESCE(t.content, rn.content_original) AS content
            FROM news_events ne
            JOIN raw_news rn ON rn.id = ne.raw_news_id
            LEFT JOIN translations t ON t.raw_news_id = rn.id
            LEFT JOIN languages l ON l.id = rn.language_id
            WHERE l.code = $1
            AND (
                (t.content IS NOT NULL AND LENGTH(t.content) > 50)
                OR (rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 50)
            )
            ORDER BY ne.id DESC
            LIMIT 1
        """, lang_code)
        
        if sample:
            print(f"\n{lang_code.upper()} - Event {sample['event_id']}:")
            print(f"  Title: {sample['title_original'][:60]}")
            print(f"  Content preview: {sample['content'][:100]}...")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
