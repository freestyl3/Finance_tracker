from typing import Annotated

from fastapi import Depends

from src.core.uow import IUnitOfWork
from src.database.dependencies import get_uow
from src.transfers.service import TransferService

def get_transfer_service(
        uow: IUnitOfWork = Depends(get_uow)
) -> TransferService:
    return TransferService(uow)

TransferServiceDep = Annotated[
    TransferService,
    Depends(get_transfer_service)
]
