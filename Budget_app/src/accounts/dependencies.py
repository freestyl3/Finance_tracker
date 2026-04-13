from typing import Annotated

from fastapi import Depends

from src.accounts.service import AccountService
from src.core.uow import IUnitOfWork
from src.infrasturcture.dependencies import get_uow

async def get_account_service(
        uow: IUnitOfWork = Depends(get_uow)
) -> AccountService:
    return AccountService(uow)

AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
