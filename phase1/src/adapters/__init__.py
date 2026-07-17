"""Source adapters mapping exports/fixtures → canonical feedback records."""

from __future__ import annotations

from .app_store import AppStoreAdapter
from .base import SourceAdapter
from .community_forums import CommunityForumsAdapter
from .play_store import PlayStoreAdapter
from .product_reviews import ProductReviewsAdapter
from .quick_commerce import QuickCommerceAdapter
from .reddit import RedditAdapter
from .social_media import SocialMediaAdapter

ADAPTERS: dict[str, type[SourceAdapter]] = {
    "play_store": PlayStoreAdapter,
    "app_store": AppStoreAdapter,
    "reddit": RedditAdapter,
    "product_reviews": ProductReviewsAdapter,
    "social_media": SocialMediaAdapter,
    "community_forums": CommunityForumsAdapter,
    "quick_commerce_discussions": QuickCommerceAdapter,
}

SOURCE_PRIORITY = list(ADAPTERS.keys())

__all__ = [
    "ADAPTERS",
    "SOURCE_PRIORITY",
    "SourceAdapter",
    "PlayStoreAdapter",
    "AppStoreAdapter",
    "RedditAdapter",
    "ProductReviewsAdapter",
    "SocialMediaAdapter",
    "CommunityForumsAdapter",
    "QuickCommerceAdapter",
]
