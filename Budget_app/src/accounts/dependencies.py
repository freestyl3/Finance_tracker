from typing import Annotated

from fastapi import Depends

from src.accounts.repository import AccountRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.operations.repositories.repository import OperationRepository
from src.database.repositories import (
    get_account_repository, get_operation_repository,
    get_user_category_repository
)
from src.accounts.service import AccountService

def get_account_service(
        account_repository: AccountRepository = Depends(get_account_repository),
        user_category_repository: UserCategoryRepository = Depends(get_user_category_repository),
        operation_repository: OperationRepository = Depends(get_operation_repository)
) -> AccountService:
    return AccountService(
        account_repository=account_repository,
        user_category_repository=user_category_repository,
        operation_repository=operation_repository
    )

AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
