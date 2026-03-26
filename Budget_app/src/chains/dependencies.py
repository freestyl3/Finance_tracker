from typing import Annotated

from fastapi import Depends

from src.chains.repository import ChainRepository
from src.accounts.repository import AccountRepository
from src.operations.repositories.operation_chain_repository import OperationChainRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.database.repositories import (
    get_chain_repository, get_account_repository,
    get_operation_chain_repository, get_user_category_repository
)
from src.chains.service import ChainService

def get_chain_service(
        chain_repository: ChainRepository = Depends(get_chain_repository),
        account_repository: AccountRepository = Depends(get_account_repository),
        operation_repository: OperationChainRepository = Depends(get_operation_chain_repository),
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
