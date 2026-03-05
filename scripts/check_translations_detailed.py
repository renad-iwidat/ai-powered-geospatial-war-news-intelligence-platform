"""
Check translations in detail
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    print("=" * 80)
    print("TRANSLATIONS ANALYSIS:")
    print("=" * 80)
    
    # Check translations by language
    trans_by_lang = await conn.fetch("""
        SELECT 
            l.code as original_lang,
            l.name as language_name,
            COUNT(DISTINCT t.raw_news_id) as translated_count,
            COUNT(DISTINCT rn.id) as total_news
        FROM raw_news rn
        LEFT JOIN languages l ON l.id = rn.language_id
        LEFT JOIN translations t ON t.raw_news_id = rn.id
        GROUP BY l.code, l.name
        ORDER BY total_news DESC
    """)
    
    print("\nTranslations by language:")
    for r in trans_by_lang:
        print(f"  {r['original_lang']}: {r['translated_count']}/{r['total_news']} translated")
    
    # Check recent translations
    print("\n" + "=" * 80)
    print("RECENT TRANSLATIONS (last 20):")
    print("=" * 80)
    
    recent_trans = await conn.fetch("""
        SELECT 
            rn.id,
            l.code as original_lang,
            rn.title_original,
            t.title as translated_title,
            LENGTH(rn.content_original) as original_len,
            LENGTH(t.content) as translated_len
        FROM translations t
        JOIN raw_news rn ON rn.id = t.raw_news_id
        LEFT JOIN languages l ON l.id = rn.language_id
        ORDER BY t.created_at DESC
        LIMIT 20
    """)
    
    for r in recent_trans:
        print(f"\nID {r['id']} ({r['original_lang']}):")
        print(f"  Original: {r['title_original'][:60]}")
        print(f"  Translated: {r['translated_title'][:60]}")
        print(f"  Lengths: {r['original_len']} → {r['translated_len']}")
    
    # Check what metrics_processor will read
    print("\n" + "=" * 80)
    print("WHAT METRICS PROCESSOR READS (sample 10 events):")
    print("=" * 80)
    
    processor_data = await conn.fetch("""
        SELECT
            ne.id AS event_id,
            ne.place_name,
            l.code as original_lang,
            COALESCE(t.content, rn.content_original) AS content,
            LENGTH(COALESCE(t.content, rn.content_original)) as content_len,
            CASE 
                WHEN t.content IS NOT NULL THEN 'TRANSLATION'
                WHEN rn.content_original IS NOT NULL THEN 'ORIGINAL'
                ELSE 'NONE'
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
        LIMIT 10
    """)
    
    for r in processor_data:
        print(f"\nEvent {r['event_id']} ({r['original_lang']}) - {r['place_name']}:")
        print(f"  Source: {r['source']}")
        print(f"  Content length: {r['content_len']}")
        if r['content']:
            print(f"  Preview: {r['content'][:100]}...")
    
    # Count events with content
    print("\n" + "=" * 80)
    print("EVENTS WITH CONTENT FOR METRICS EXTRACTION:")
    print("=" * 80)
    
    stats = await conn.fetchrow("""
        SELECT
            COUNT(*) as total_events,
            COUNT(CASE WHEN t.content IS NOT NULL AND LENGTH(t.content) > 50 THEN 1 END) as from_translation,
            COUNT(CASE WHEN t.content IS NULL AND rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 50 THEN 1 END) as from_original,
            COUNT(CASE WHEN (t.content IS NOT NULL AND LENGTH(t.content) > 50) OR (rn.content_original IS NOT NULL AND LENGTH(rn.content_original) > 50) THEN 1 END) as with_content
        FROM news_events ne
        JOIN raw_news rn ON rn.id = ne.raw_news_id
        LEFT JOIN translations t ON t.raw_news_id = rn.id
    """)
    
    print(f"Total events: {stats['total_events']}")
    print(f"With content from translation: {stats['from_translation']}")
    print(f"With content from original: {stats['from_original']}")
    print(f"Total with content: {stats['with_content']}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
