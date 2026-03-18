from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_helper import db_helper
from src.chains.repository import ChainRepository
from src.chains.service import ChainService
from src.accounts.repository import AccountRepository
from src.accounts.dependencies import get_account_repository
from src.operations.repository import OperationRepository
from src.operations.dependencies import get_operation_repository
from src.categories.user_categories.repository import UserCategoryRepository
from src.categories.user_categories.dependecies import get_user_category_repository

def get_chain_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> ChainRepository:
    return ChainRepository(session)

def get_chain_service(
        chain_repository: ChainRepository = Depends(get_chain_repository),
        account_repository: AccountRepository = Depends(get_account_repository),
        operation_repository: OperationRepository = Depends(get_operation_repository),
        category_repository: UserCategoryRepository = Depends(get_user_category_repository)
) -> ChainService:
    return ChainService(
        chain_repository=chain_repository,
        account_repository=account_repository,
        operation_repository=operation_repository,
        category_repository=category_repository
    )

ChainServiceDep = Annotated[
    ChainService,
    Depends(get_chain_service)
]
