from typing import Annotated

from fastapi import Depends

from src.categories.system_categories.repository import SystemCategoryRepository
from src.database.repositories import get_system_category_repository
from src.categories.system_categories.service import SystemCategoryService

def get_system_category_service(
        repo: SystemCategoryRepository = Depends(get_system_category_repository)
) -> SystemCategoryService:
    return SystemCategoryService(repo)

SystemCategoryServiceDep = Annotated[
    SystemCategoryService,
    Depends(get_system_category_service)
]
