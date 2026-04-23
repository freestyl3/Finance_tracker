from typing import Annotated

from fastapi import Depends

from src.core.uow import IUnitOfWork
from src.database.dependencies import get_uow
from src.feed.service import FeedService

async def get_feed_service(uow: IUnitOfWork = Depends(get_uow)) -> FeedService:
    return FeedService(uow)

FeedServiceDep = Annotated[
    FeedService,
    Depends(get_feed_service)
]