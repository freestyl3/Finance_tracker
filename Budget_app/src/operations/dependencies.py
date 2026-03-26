from typing import Annotated

from fastapi import Depends

from src.operations.repositories.repository import OperationRepository
from src.accounts.repository import AccountRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.operations.transfer_repository import TransferRepository
from src.database.repositories import(
    get_operation_repository, get_account_repository, get_transfer_repository,
    get_user_category_repository
)
from src.operations.service import OperationService
from src.operations.transfer_service import TransferService

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
