#!/usr/bin/env python3
"""
Check today's articles and their status
"""

import asyncio
import asyncpg
from datetime import date, timedelta
import sys

async def check_today_articles():
    """Check today's articles"""
    
    # Get database URL from environment
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env", file=sys.stderr)
        return False
    
    # Connect to database
    try:
        conn = await asyncpg.connect(database_url)
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}", file=sys.stderr)
        return False
    
    try:
        today = date.today()
        
        print(f"📅 Checking articles for {today}")
        print()
        
        # Get today's articles
        rows = await conn.fetch(
            """
            SELECT
                rn.id,
                rn.title_original,
                rn.language_id,
                rn.has_numbers,
                COALESCE(rn.published_at, rn.fetched_at) as date,
                (SELECT COUNT(*) FROM news_events ne WHERE ne.raw_news_id = rn.id) as events_count,
                (SELECT COUNT(*) FROM translations t WHERE t.raw_news_id = rn.id) as translations_count
            FROM raw_news rn
            WHERE DATE(COALESCE(rn.published_at, rn.fetched_at)) = $1
            ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC
            """,
            today
        )
        
        print(f"✅ Found {len(rows)} articles for today")
        print()
        
        # Get language info
        ar_lang = await conn.fetchrow("SELECT id FROM languages WHERE code='ar'")
        ar_id = ar_lang['id'] if ar_lang else None
        
        print(f"Arabic language ID: {ar_id}")
        print()
        
        # Categorize articles
        arabic_articles = []
        translated_articles = []
        no_translation = []
        with_events = []
        without_events = []
        
        for row in rows:
            if row['events_count'] > 0:
                with_events.append(row)
            else:
                without_events.append(row)
            
            if row['language_id'] == ar_id:
                arabic_articles.append(row)
            
            if row['translations_count'] > 0:
                translated_articles.append(row)
            else:
                no_translation.append(row)
        
        print(f"📊 Article Breakdown:")
        print(f"  - Arabic articles: {len(arabic_articles)}")
        print(f"  - Translated articles: {len(translated_articles)}")
        print(f"  - No translation: {len(no_translation)}")
        print(f"  - With events: {len(with_events)}")
        print(f"  - Without events: {len(without_events)}")
        print()
        
        # Show articles that need processing
        print(f"📋 Articles that need location extraction (no events):")
        eligible = [r for r in without_events if r['language_id'] == ar_id or r['translations_count'] > 0]
        print(f"  - Eligible: {len(eligible)}")
        
        if eligible:
            print(f"\n  First 5 eligible articles:")
            for i, row in enumerate(eligible[:5], 1):
                lang_type = "Arabic" if row['language_id'] == ar_id else "Translated"
                print(f"    {i}. ID={row['id']} ({lang_type}) - {row['title_original'][:60]}...")
        
        print()
        print(f"❌ Articles that CANNOT be processed (not Arabic, no translation):")
        ineligible = [r for r in without_events if r['language_id'] != ar_id and r['translations_count'] == 0]
        print(f"  - Ineligible: {len(ineligible)}")
        
        if ineligible:
            print(f"\n  First 5 ineligible articles:")
            for i, row in enumerate(ineligible[:5], 1):
                print(f"    {i}. ID={row['id']} - {row['title_original'][:60]}...")
        
        return True
    
    finally:
        await conn.close()

if __name__ == "__main__":
    success = asyncio.run(check_today_articles())
    sys.exit(0 if success else 1)
