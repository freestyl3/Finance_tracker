from typing import Annotated

from fastapi import Depends

from src.core.uow import IUnitOfWork
from src.database.dependencies import get_uow
from src.chains.service import ChainService

async def get_chain_service(
        uow: IUnitOfWork = Depends(get_uow)
) -> ChainService:
    return ChainService(uow)

ChainServiceDep = Annotated[
    ChainService,
    Depends(get_chain_service)
]
