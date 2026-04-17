from typing import Annotated

from fastapi import Depends

from src.core.uow import IUnitOfWork
from src.database.dependencies import get_uow
from src.categories.user_categories.service import UserCategoryService

def get_user_category_service(
        uow: IUnitOfWork = Depends(get_uow)
) -> UserCategoryService:
    return UserCategoryService(uow)

UserCategoryServiceDep = Annotated[
    UserCategoryService,
    Depends(get_user_category_service)
]
