from typing import Annotated

from fastapi import Depends

from src.categories.user_categories.repository import UserCategoryRepository
from src.database.repositories import get_user_category_repository
from src.categories.user_categories.service import UserCategoryService

def get_user_category_service(
        repo: UserCategoryRepository = Depends(get_user_category_repository)
) -> UserCategoryService:
    return UserCategoryService(repo)

UserCategoryServiceDep = Annotated[
    UserCategoryService,
    Depends(get_user_category_service)
]
