"""
Analyze news data in database
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Get total statistics
    print("=" * 80)
    print("DATABASE STATISTICS:")
    print("=" * 80)
    
    stats = await conn.fetchrow("""
        SELECT 
            COUNT(*) as total_news,
            COUNT(CASE WHEN content_original IS NOT NULL AND LENGTH(content_original) > 100 THEN 1 END) as with_content,
            COUNT(CASE WHEN has_numbers = true THEN 1 END) as with_numbers,
            COUNT(CASE WHEN language_id = 1 THEN 1 END) as arabic_news
        FROM raw_news
    """)
    
    print(f"Total news: {stats['total_news']}")
    print(f"With content (>100 chars): {stats['with_content']}")
    print(f"With numbers: {stats['with_numbers']}")
    print(f"Arabic news: {stats['arabic_news']}")
    
    # Get latest 30 news
    print("\n" + "=" * 80)
    print("LATEST 30 NEWS:")
    print("=" * 80)
    
    latest = await conn.fetch("""
        SELECT 
            rn.id,
            rn.title_original,
            LEFT(rn.content_original, 200) as content_preview,
            rn.published_at,
            rn.has_numbers,
            s.name as source_name,
            l.code as language
        FROM raw_news rn
        LEFT JOIN sources s ON s.id = rn.source_id
        LEFT JOIN languages l ON l.id = rn.language_id
        ORDER BY rn.id DESC
        LIMIT 30
    """)
    
    war_keywords = ['حرب', 'صاروخ', 'قصف', 'غارة', 'قتل', 'مقتل', 'عسكري', 'جيش', 'هجوم', 'ضربة', 'إيران', 'إسرائيل']
    
    war_count = 0
    non_war_count = 0
    
    for i, news in enumerate(latest, 1):
        title = news['title_original'] or ""
        content = news['content_preview'] or ""
        
        # Check if war-related
        is_war = any(keyword in title or keyword in content for keyword in war_keywords)
        
        if is_war:
            war_count += 1
            category = "⚔️ WAR"
        else:
            non_war_count += 1
            category = "📰 OTHER"
        
        print(f"\n{i}. [{category}] ID: {news['id']} | Source: {news['source_name']}")
        print(f"   Title: {title[:100]}")
        print(f"   Has numbers: {news['has_numbers']}")
        if content:
            print(f"   Preview: {content[:150]}...")
    
    print("\n" + "=" * 80)
    print(f"Summary: {war_count} war-related, {non_war_count} other topics")
    print("=" * 80)
    
    # Check sources
    print("\n" + "=" * 80)
    print("NEWS SOURCES:")
    print("=" * 80)
    
    sources = await conn.fetch("""
        SELECT 
            s.name,
            s.url,
            COUNT(rn.id) as news_count
        FROM sources s
        LEFT JOIN raw_news rn ON rn.source_id = s.id
        WHERE s.is_active = true
        GROUP BY s.id, s.name, s.url
        ORDER BY news_count DESC
    """)
    
    for src in sources:
        print(f"\n{src['name']}: {src['news_count']} news")
        print(f"  URL: {src['url']}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
