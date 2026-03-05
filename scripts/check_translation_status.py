"""
Check why recent news are not translated
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    print("=" * 80)
    print("TRANSLATION STATUS:")
    print("=" * 80)
    
    # Check recent Arabic news without translations
    recent = await conn.fetch("""
        SELECT 
            rn.id,
            rn.title_original,
            rn.language_id,
            l.code as language,
            CASE WHEN t.id IS NOT NULL THEN 'YES' ELSE 'NO' END as has_translation
        FROM raw_news rn
        LEFT JOIN languages l ON l.id = rn.language_id
        LEFT JOIN translations t ON t.raw_news_id = rn.id
        WHERE rn.id >= 380
        ORDER BY rn.id DESC
    """)
    
    print("\nRecent news (ID >= 380):")
    arabic_without_trans = 0
    arabic_with_trans = 0
    
    for news in recent:
        status = "✅" if news['has_translation'] == 'YES' else "❌"
        print(f"{status} ID: {news['id']} | Lang: {news['language']} | {news['title_original'][:60]}")
        
        if news['language'] == 'ar':
            if news['has_translation'] == 'YES':
                arabic_with_trans += 1
            else:
                arabic_without_trans += 1
    
    print(f"\nArabic news: {arabic_with_trans} with translation, {arabic_without_trans} without")
    
    # Check if there's a translation process
    print("\n" + "=" * 80)
    print("QUESTION: Are Arabic news supposed to be translated?")
    print("=" * 80)
    print("Arabic news are already in Arabic, so they don't need translation!")
    print("The 'translations' table is for translating non-Arabic news TO Arabic.")
    print("\nFor metrics extraction, we should:")
    print("1. Use content_original for Arabic news")
    print("2. Use translations.content for non-Arabic news")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
