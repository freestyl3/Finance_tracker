from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_helper import db_helper
from src.categories.system_categories.repository import SystemCategoryRepository
from src.categories.system_categories.service import SystemCategoryService

async def get_system_category_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> SystemCategoryRepository:
    return SystemCategoryRepository(session)

async def get_system_category_service(
        repo: SystemCategoryRepository = Depends(get_system_category_repository)
) -> SystemCategoryService:
    return SystemCategoryService(repo)

SystemCategoryServiceDep = Annotated[
    SystemCategoryService,
    Depends(get_system_category_service)
]
