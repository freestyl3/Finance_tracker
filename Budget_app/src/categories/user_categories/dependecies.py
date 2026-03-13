from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_helper import db_helper
from src.categories.user_categories.repository import UserCategoryRepository
from src.categories.user_categories.service import UserCategoryService

async def get_user_category_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> UserCategoryRepository:
    return UserCategoryRepository(session)

async def get_user_category_service(
        repo: UserCategoryRepository = Depends(get_user_category_repository)
) -> UserCategoryService:
    return UserCategoryService(repo)

UserCategoryServiceDep = Annotated[
    UserCategoryService,
    Depends(get_user_category_service)
]
