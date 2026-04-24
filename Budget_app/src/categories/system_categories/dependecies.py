from typing import Annotated

from fastapi import Depends

from src.core.uow import IUnitOfWork
from src.database.dependencies import get_uow
from src.categories.system_categories.service import SystemCategoryService

def get_system_category_service(
        uow: IUnitOfWork = Depends(get_uow)
) -> SystemCategoryService:
    return SystemCategoryService(uow)

SystemCategoryServiceDep = Annotated[
    SystemCategoryService,
    Depends(get_system_category_service)
]
