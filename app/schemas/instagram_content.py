from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class InstagramMediaInsight(BaseModel):
    """Instagram media insights"""
    impressions: Optional[int] = None
    reach: Optional[int] = None
    engagement: Optional[int] = None


class InstagramMedia(BaseModel):
    """Instagram media (Reel or Post)"""
    id: str
    caption: Optional[str] = None
    media_type: str  # IMAGE, VIDEO, CAROUSEL, REELS
    media_url: Optional[str] = None
    permalink: Optional[str] = None
    timestamp: datetime
    like_count: Optional[int] = None
    comments_count: Optional[int] = None
    insights: Optional[InstagramMediaInsight] = None


class InstagramBusinessAccount(BaseModel):
    """Instagram business account info"""
    id: str
    name: Optional[str] = None
    biography: Optional[str] = None
    followers_count: Optional[int] = None
    follows_count: Optional[int] = None
    media_count: Optional[int] = None
    profile_picture_url: Optional[str] = None
    website: Optional[str] = None


class InstagramFeedResponse(BaseModel):
    """Response for Instagram feed"""
    account: InstagramBusinessAccount
    media: List[InstagramMedia]
    total_count: int
    last_updated: datetime
    next_update_in_minutes: int
