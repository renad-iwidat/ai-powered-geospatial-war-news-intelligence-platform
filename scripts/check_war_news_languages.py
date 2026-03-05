"""
Check war news languages
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Get war-related news
    print("=" * 80)
    print("WAR-RELATED NEWS BY LANGUAGE:")
    print("=" * 80)
    
    war_keywords = ['حرب', 'صاروخ', 'قصف', 'غارة', 'قتل', 'مقتل', 'عسكري', 'جيش', 'هجوم', 'ضربة', 'إيران', 'إسرائيل',
                    'war', 'missile', 'strike', 'attack', 'military', 'iran', 'israel',
                    'מלחמה', 'טיל', 'תקיפה', 'צבא', 'איראן', 'ישראל']
    
    # Get all news
    all_news = await conn.fetch("""
        SELECT 
            rn.id,
            rn.title_original,
            rn.content_original,
            l.code as language,
            l.name as language_name,
            s.name as source_name
        FROM raw_news rn
        LEFT JOIN languages l ON l.id = rn.language_id
        LEFT JOIN sources s ON s.id = rn.source_id
        ORDER BY rn.id DESC
        LIMIT 100
    """)
    
    war_news_by_lang = {'ar': 0, 'en': 0, 'he': 0, 'unknown': 0}
    total_by_lang = {'ar': 0, 'en': 0, 'he': 0, 'unknown': 0}
    
    for news in all_news:
        title = news['title_original'] or ""
        content = news['content_original'] or ""
        lang = news['language'] or 'unknown'
        
        # Count by language
        if lang in total_by_lang:
            total_by_lang[lang] += 1
        else:
            total_by_lang['unknown'] += 1
        
        # Check if war-related
        is_war = any(keyword in title.lower() or keyword in content.lower() for keyword in war_keywords)
        
        if is_war:
            if lang in war_news_by_lang:
                war_news_by_lang[lang] += 1
            else:
                war_news_by_lang['unknown'] += 1
    
    print("\nTotal news by language (last 100):")
    for lang, count in total_by_lang.items():
        print(f"  {lang}: {count}")
    
    print("\nWar-related news by language:")
    for lang, count in war_news_by_lang.items():
        print(f"  {lang}: {count}")
    
    # Check translations
    print("\n" + "=" * 80)
    print("TRANSLATIONS STATUS:")
    print("=" * 80)
    
    trans_stats = await conn.fetchrow("""
        SELECT 
            COUNT(DISTINCT raw_news_id) as translated_news,
            COUNT(*) as total_translations
        FROM translations
    """)
    
    print(f"News with translations: {trans_stats['translated_news']}")
    print(f"Total translations: {trans_stats['total_translations']}")
    
    # Sample war news in different languages
    print("\n" + "=" * 80)
    print("SAMPLE WAR NEWS:")
    print("=" * 80)
    
    samples = await conn.fetch("""
        SELECT 
            rn.id,
            rn.title_original,
            LEFT(rn.content_original, 200) as content,
            l.code as language,
            t.title as translated_title,
            LEFT(t.content, 200) as translated_content
        FROM raw_news rn
        LEFT JOIN languages l ON l.id = rn.language_id
        LEFT JOIN translations t ON t.raw_news_id = rn.id
        WHERE rn.id IN (402, 401, 400, 394, 392, 388, 387, 386, 381, 380)
        ORDER BY rn.id DESC
    """)
    
    for news in samples:
        print(f"\nID: {news['id']} | Language: {news['language']}")
        print(f"Title: {news['title_original'][:80]}")
        if news['translated_title']:
            print(f"Translated: {news['translated_title'][:80]}")
        else:
            print("⚠️ No translation")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
