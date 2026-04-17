from fastapi import Depends

from src.database.db_helper import db_helper
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import UserRepository
from src.accounts.repository import AccountRepository
from src.categories.system_categories.repository import SystemCategoryRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.operations.repository import OperationRepository
from src.transfers.repository import TransferRepository
from src.chains.repository import ChainRepository
from src.feed.repository import FeedRepository

async def get_account_repository(
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> AccountRepository:
    return AccountRepository(session)

async def get_user_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> UserRepository:
    return UserRepository(session)

async def get_system_category_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> SystemCategoryRepository:
    return SystemCategoryRepository(session)

async def get_user_category_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> UserCategoryRepository:
    return UserCategoryRepository(session)

async def get_operation_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> OperationRepository:
    return OperationRepository(session)

async def get_transfer_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> TransferRepository:
    return TransferRepository(session)

async def get_chain_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> ChainRepository:
    return ChainRepository(session)

async def get_feed_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> FeedRepository:
    return FeedRepository(session)
