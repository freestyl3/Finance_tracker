from typing import Annotated

from fastapi import Depends

from src.feed.repository import FeedRepository
from src.database.repositories import get_feed_repository
from src.feed.service import FeedService

async def get_feed_service(
        feed_repository: FeedRepository = Depends(get_feed_repository)
) -> FeedService:
    return FeedService(repo=feed_repository)

FeedServiceDep = Annotated[
    FeedService,
    Depends(get_feed_service)
]