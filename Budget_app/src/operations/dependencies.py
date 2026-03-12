from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_helper import db_helper
from src.operations.repository import OperationRepository
from src.operations.service import OperationService
from src.accounts.repository import AccountRepository
from src.accounts.dependencies import get_account_repository
from src.categories.user_categories.repository import UserCategoryRepository
from src.categories.user_categories.dependecies import get_user_category_repository
from src.operations.transfer_repository import TransferRepository
from src.operations.transfer_service import TransferService

def get_operation_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
    ) -> OperationRepository:
    return OperationRepository(session)

def get_transfer_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> TransferRepository:
    return TransferRepository(session)

def get_operation_service(
        operation_repo: OperationRepository = Depends(get_operation_repository),
        account_repo: AccountRepository = Depends(get_account_repository),
        user_category_repo: UserCategoryRepository = Depends(get_user_category_repository)
) -> OperationService:
    return OperationService(operation_repo, user_category_repo, account_repo)

def get_transfer_service(
        transfer_repo: TransferRepository = Depends(get_transfer_repository),
        operation_repo: OperationRepository = Depends(get_operation_repository),
        account_repo: AccountRepository = Depends(get_account_repository),
        user_category_repo: UserCategoryRepository = Depends(get_user_category_repository)
) -> TransferService:
    return TransferService(
        repo=transfer_repo,
        operation_repository=operation_repo,
        user_category_repository=user_category_repo,
        account_repository=account_repo
    )

OperationServiceDep = Annotated[
    OperationService,
    Depends(get_operation_service)
]

TransferServiceDep = Annotated[
    TransferService,
    Depends(get_transfer_service)
]
