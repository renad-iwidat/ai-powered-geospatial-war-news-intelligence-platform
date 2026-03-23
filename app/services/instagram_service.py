import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.schemas.instagram_content import (
    InstagramMedia,
    InstagramBusinessAccount,
    InstagramMediaInsight,
)

logger = logging.getLogger(__name__)

# In-memory cache for Instagram data
_instagram_cache: Dict[str, Any] = {
    "data": None,
    "last_updated": None,
    "account": None,
}


class InstagramService:
    """Service for fetching Instagram business account data"""

    BASE_URL = f"https://graph.instagram.com/{settings.INSTAGRAM_API_VERSION}"

    @classmethod
    async def get_account_info(cls) -> Optional[InstagramBusinessAccount]:
        """Fetch Instagram business account information"""
        try:
            url = f"{cls.BASE_URL}/{settings.INSTAGRAM_BUSINESS_ACCOUNT_ID}"
            params = {
                "fields": "id,name,biography,followers_count,follows_count,media_count,profile_picture_url,website",
                "access_token": settings.INSTAGRAM_ACCESS_TOKEN,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                return InstagramBusinessAccount(
                    id=data.get("id"),
                    name=data.get("name"),
                    biography=data.get("biography"),
                    followers_count=data.get("followers_count"),
                    follows_count=data.get("follows_count"),
                    media_count=data.get("media_count"),
                    profile_picture_url=data.get("profile_picture_url"),
                    website=data.get("website"),
                )
        except Exception as e:
            logger.error(f"Error fetching Instagram account info: {str(e)}")
            return None

    @classmethod
    async def get_latest_media(cls, limit: int = 10) -> List[InstagramMedia]:
        """Fetch latest media (Reels and Posts) from business account"""
        try:
            url = f"{cls.BASE_URL}/{settings.INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
            params = {
                "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count",
                "limit": limit,
                "access_token": settings.INSTAGRAM_ACCESS_TOKEN,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                media_list = []
                for item in data.get("data", []):
                    # Filter for Reels and Posts only
                    if item.get("media_type") in ["REELS", "VIDEO", "IMAGE", "CAROUSEL"]:
                        media = InstagramMedia(
                            id=item.get("id"),
                            caption=item.get("caption"),
                            media_type=item.get("media_type"),
                            media_url=item.get("media_url"),
                            permalink=item.get("permalink"),
                            timestamp=datetime.fromisoformat(
                                item.get("timestamp", "").replace("Z", "+00:00")
                            ),
                            like_count=item.get("like_count"),
                            comments_count=item.get("comments_count"),
                        )
                        media_list.append(media)

                return media_list[:limit]
        except Exception as e:
            logger.error(f"Error fetching Instagram media: {str(e)}")
            return []

    @classmethod
    async def get_media_insights(cls, media_id: str) -> Optional[InstagramMediaInsight]:
        """Fetch insights for a specific media"""
        try:
            url = f"{cls.BASE_URL}/{media_id}/insights"
            params = {
                "metric": "impressions,reach,engagement",
                "access_token": settings.INSTAGRAM_ACCESS_TOKEN,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                insights_data = {}
                for metric in data.get("data", []):
                    metric_name = metric.get("name")
                    metric_value = metric.get("values", [{}])[0].get("value")
                    insights_data[metric_name] = metric_value

                return InstagramMediaInsight(
                    impressions=insights_data.get("impressions"),
                    reach=insights_data.get("reach"),
                    engagement=insights_data.get("engagement"),
                )
        except Exception as e:
            logger.error(f"Error fetching media insights for {media_id}: {str(e)}")
            return None

    @classmethod
    async def get_feed_with_cache(cls) -> Dict[str, Any]:
        """Get Instagram feed with caching (updates every 15 minutes)"""
        now = datetime.utcnow()
        cache_duration = timedelta(minutes=settings.INSTAGRAM_CACHE_DURATION_MINUTES)

        # Check if cache is still valid
        if (
            _instagram_cache["data"] is not None
            and _instagram_cache["last_updated"] is not None
            and (now - _instagram_cache["last_updated"]) < cache_duration
        ):
            time_until_next_update = cache_duration - (
                now - _instagram_cache["last_updated"]
            )
            return {
                "data": _instagram_cache["data"],
                "account": _instagram_cache["account"],
                "cached": True,
                "next_update_in_minutes": int(time_until_next_update.total_seconds() / 60),
            }

        # Fetch fresh data
        logger.info("Fetching fresh Instagram data...")
        account = await cls.get_account_info()
        media_list = await cls.get_latest_media(limit=10)

        # Optionally fetch insights for each media (can be slow)
        # for media in media_list:
        #     insights = await cls.get_media_insights(media.id)
        #     if insights:
        #         media.insights = insights

        # Update cache
        _instagram_cache["data"] = [m.model_dump() for m in media_list]
        _instagram_cache["account"] = account.model_dump() if account else None
        _instagram_cache["last_updated"] = now

        return {
            "data": _instagram_cache["data"],
            "account": _instagram_cache["account"],
            "cached": False,
            "next_update_in_minutes": settings.INSTAGRAM_CACHE_DURATION_MINUTES,
        }
