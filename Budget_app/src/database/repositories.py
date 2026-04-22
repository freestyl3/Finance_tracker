from fastapi import Depends

from src.database.db_helper import db_helper
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import UserRepository
from src.operations.repository import OperationRepository
from src.feed.repository import FeedRepository

async def get_user_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> UserRepository:
    return UserRepository(session)

async def get_operation_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> OperationRepository:
    return OperationRepository(session)

async def get_feed_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> FeedRepository:
    return FeedRepository(session)
