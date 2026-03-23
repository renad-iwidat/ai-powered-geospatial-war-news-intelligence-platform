#!/usr/bin/env python3
"""
Test script for Instagram API integration
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.instagram_service import InstagramService
from app.core.config import settings


async def test_instagram_api():
    """Test Instagram API endpoints"""
    
    print("=" * 60)
    print("Instagram API Integration Test")
    print("=" * 60)
    
    # Check configuration
    print("\n1. Checking Configuration...")
    print(f"   Account ID: {settings.INSTAGRAM_BUSINESS_ACCOUNT_ID}")
    print(f"   API Version: {settings.INSTAGRAM_API_VERSION}")
    print(f"   Cache Duration: {settings.INSTAGRAM_CACHE_DURATION_MINUTES} minutes")
    print(f"   Token Present: {'Yes' if settings.INSTAGRAM_ACCESS_TOKEN else 'No'}")
    
    if not settings.INSTAGRAM_ACCESS_TOKEN:
        print("\n   ⚠️  WARNING: INSTAGRAM_ACCESS_TOKEN not set in .env")
        print("   Please add your Instagram access token to .env file")
        return
    
    # Test account info
    print("\n2. Fetching Account Information...")
    try:
        account = await InstagramService.get_account_info()
        if account:
            print(f"   ✓ Account Name: {account.name}")
            print(f"   ✓ Followers: {account.followers_count}")
            print(f"   ✓ Media Count: {account.media_count}")
        else:
            print("   ✗ Failed to fetch account info")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test media fetch
    print("\n3. Fetching Latest Media (10 items)...")
    try:
        media_list = await InstagramService.get_latest_media(limit=10)
        print(f"   ✓ Found {len(media_list)} media items")
        
        for i, media in enumerate(media_list[:3], 1):
            print(f"\n   Media {i}:")
            print(f"      Type: {media.media_type}")
            print(f"      Caption: {media.caption[:50] if media.caption else 'N/A'}...")
            print(f"      Likes: {media.like_count}")
            print(f"      Comments: {media.comments_count}")
            print(f"      Posted: {media.timestamp}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test caching
    print("\n4. Testing Cache System...")
    try:
        feed1 = await InstagramService.get_feed_with_cache()
        print(f"   ✓ First call - Cached: {feed1.get('cached', False)}")
        
        feed2 = await InstagramService.get_feed_with_cache()
        print(f"   ✓ Second call - Cached: {feed2.get('cached', False)}")
        print(f"   ✓ Next update in: {feed2.get('next_update_in_minutes')} minutes")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_instagram_api())
