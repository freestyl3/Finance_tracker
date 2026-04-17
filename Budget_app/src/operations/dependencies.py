from typing import Annotated

from fastapi import Depends

from src.core.uow import IUnitOfWork
from src.database.dependencies import get_uow
from src.operations.service import OperationService

def get_operation_service(
        uow: IUnitOfWork = Depends(get_uow)
) -> OperationService:
    return OperationService(uow)

OperationServiceDep = Annotated[
    OperationService,
    Depends(get_operation_service)
]
