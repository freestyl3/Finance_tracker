from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_helper import db_helper
from src.accounts.repository import AccountRepository
from src.accounts.service import AccountService

async def get_accounts_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> AccountRepository:
    return AccountRepository(session)

async def get_accounts_service(
        repo: AsyncSession = Depends(get_accounts_repository)
) -> AccountService:
    return AccountService(repo)

AccountServiceDep = Annotated[AccountService, Depends(get_accounts_service)]
