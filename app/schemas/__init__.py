"""
Pydantic Schemas
All response and request models
"""

from app.schemas.news_article import (
    NewsArticleBase,
    NewsArticleListItem,
    NewsArticleDetail,
    NewsArticleListResponse,
    NewsArticleBySource,
    NewsArticlesBySourceResponse
)

from app.schemas.geographic_location import (
    GeographicLocationBase,
    GeographicLocationListItem,
    GeographicLocationDetail,
    GeographicLocationListResponse
)

from app.schemas.news_event import (
    NewsEventBase,
    NewsEventListItem,
    NewsEventDetail,
    NewsEventListResponse
)

from app.schemas.event_metric import (
    EventMetricBase,
    EventMetricListItem,
    EventMetricSummary,
    EventMetricListResponse,
    EventMetricSummaryResponse
)

from app.schemas.analytics import (
    AnalyticsOverview,
    CountryStatistics,
    CountryStatisticsResponse,
    DateStatistics,
    DateStatisticsResponse,
    TimelineItem,
    TimelineResponse
)

from app.schemas.data_processing import (
    LocationExtractionRequest,
    LocationExtractionResponse,
    MetricsExtractionRequest,
    MetricsExtractionResponse,
    ProcessingStatus
)

from app.schemas.source import (
    SourceBase,
    SourceDetail,
    SourceListItem,
    SourceListResponse,
    SourceStatusResponse
)

from app.schemas.instagram_content import (
    InstagramMedia,
    InstagramBusinessAccount,
    InstagramMediaInsight,
    InstagramFeedResponse
)

__all__ = [
    # News Articles
    "NewsArticleBase",
    "NewsArticleListItem",
    "NewsArticleDetail",
    "NewsArticleListResponse",
    "NewsArticleBySource",
    "NewsArticlesBySourceResponse",
    
    # Geographic Locations
    "GeographicLocationBase",
    "GeographicLocationListItem",
    "GeographicLocationDetail",
    "GeographicLocationListResponse",
    
    # News Events
    "NewsEventBase",
    "NewsEventListItem",
    "NewsEventDetail",
    "NewsEventListResponse",
    
    # Event Metrics
    "EventMetricBase",
    "EventMetricListItem",
    "EventMetricSummary",
    "EventMetricListResponse",
    "EventMetricSummaryResponse",
    
    # Analytics
    "AnalyticsOverview",
    "CountryStatistics",
    "CountryStatisticsResponse",
    "DateStatistics",
    "DateStatisticsResponse",
    "TimelineItem",
    "TimelineResponse",
    
    # Data Processing
    "LocationExtractionRequest",
    "LocationExtractionResponse",
    "MetricsExtractionRequest",
    "MetricsExtractionResponse",
    "ProcessingStatus",
    
    # Sources
    "SourceBase",
    "SourceDetail",
    "SourceListItem",
    "SourceListResponse",
    "SourceStatusResponse",
    
    # Instagram
    "InstagramMedia",
    "InstagramBusinessAccount",
    "InstagramMediaInsight",
    "InstagramFeedResponse",
]
