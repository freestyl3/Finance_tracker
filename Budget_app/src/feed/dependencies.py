from typing import Annotated

from fastapi import Depends

from src.feed.repository import FeedRepository
from src.database.repositories import get_feed_repository
from src.operations.repositories.operation_chain_repository import OperationChainRepository
from src.database.repositories import get_operation_chain_repository
from src.feed.service import FeedService

async def get_feed_service(
        feed_repository: FeedRepository = Depends(get_feed_repository),
        operation_repository: OperationChainRepository = Depends(get_operation_chain_repository)
) -> FeedService:
    return FeedService(
        repository=feed_repository,
        operation_repository=operation_repository
    )

FeedServiceDep = Annotated[
    FeedService,
    Depends(get_feed_service)
]