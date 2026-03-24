"""
Instagram Feed Endpoint
Provides access to latest Instagram Reels and Posts from business account
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from app.services.instagram_service import InstagramService
from app.schemas.instagram_content import InstagramFeedResponse, InstagramMedia
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/feed", response_model=dict)
async def get_instagram_feed(
    limit: int = Query(10, ge=1, le=50, description="Number of media items to return"),
    include_insights: bool = Query(False, description="Include engagement insights"),
):
    """
    Get latest Instagram Reels and Posts from business account
    
    - **limit**: Number of media items to return (1-50, default 10)
    - **include_insights**: Whether to include engagement insights (impressions, reach, engagement)
    
    Returns cached data if updated within the last 15 minutes.
    """
    try:
        feed_data = await InstagramService.get_feed_with_cache()

        if not feed_data["account"]:
            raise HTTPException(
                status_code=503,
                detail="Unable to fetch Instagram account information. Check credentials.",
            )

        media_items = feed_data["data"][:limit]

        # If insights are requested, fetch them for each media
        if include_insights:
            for media in media_items:
                insights = await InstagramService.get_media_insights(media["id"])
                if insights:
                    media["insights"] = insights.model_dump()

        return {
            "account": feed_data["account"],
            "media": media_items,
            "total_count": len(media_items),
            "last_updated": feed_data.get("last_updated", datetime.utcnow()),
            "next_update_in_minutes": feed_data["next_update_in_minutes"],
            "cached": feed_data.get("cached", False),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Instagram feed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching Instagram feed: {str(e)}"
        )


@router.get("/account")
async def get_instagram_account():
    """
    Get Instagram business account information
    
    Returns account details like follower count, biography, profile picture, etc.
    """
    try:
        account = await InstagramService.get_account_info()

        if not account:
            raise HTTPException(
                status_code=503,
                detail="Unable to fetch Instagram account information. Check credentials.",
            )

        return account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Instagram account: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching Instagram account: {str(e)}"
        )


@router.get("/media/{media_id}/insights")
async def get_media_insights(media_id: str):
    """
    Get engagement insights for a specific media item
    
    Returns impressions, reach, and engagement metrics.
    """
    try:
        insights = await InstagramService.get_media_insights(media_id)

        if not insights:
            raise HTTPException(
                status_code=404, detail="Unable to fetch insights for this media"
            )

        return insights

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching media insights: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching media insights: {str(e)}"
        )


@router.get("/reels")
async def get_instagram_reels(
    limit: int = Query(10, ge=1, le=50, description="Number of reels to return"),
):
    """
    Get latest Instagram Reels only (filtered from all media)
    
    - **limit**: Number of reels to return (1-50, default 10)
    """
    try:
        feed_data = await InstagramService.get_feed_with_cache()

        if not feed_data["account"]:
            raise HTTPException(
                status_code=503,
                detail="Unable to fetch Instagram account information. Check credentials.",
            )

        # Filter for Reels only
        reels = [m for m in feed_data["data"] if m.get("media_type") == "REELS"][:limit]

        return {
            "account": feed_data["account"],
            "reels": reels,
            "total_count": len(reels),
            "last_updated": feed_data.get("last_updated", datetime.utcnow()),
            "next_update_in_minutes": feed_data["next_update_in_minutes"],
            "cached": feed_data.get("cached", False),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Instagram reels: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching Instagram reels: {str(e)}"
        )
