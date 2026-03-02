import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.base.service import BaseService
from src.categories.user_categories.repository import UserCategoryRepository
from src.categories.base.schemas import CategoryCreate
from src.categories.user_categories.models import UserCategory

class UserCategoryService(BaseService[UserCategoryRepository]):
    def __init__(self, repo: UserCategoryRepository):
        super().__init__(repo)

    async def create(
            self,
            category_create: CategoryCreate,
            user_id: uuid.UUID
    ) -> UserCategory | None:
        try:
            new_category = await self.repo.create(
                category_data=category_create,
                user_id=user_id
            )
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have category with this name and type!"
            )
        
        return new_category
