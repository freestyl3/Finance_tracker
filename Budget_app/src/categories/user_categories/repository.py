import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.base.repository import BaseRepository
from src.categories.base.schemas import CategoryCreate, CategoryUpdate
from src.categories.user_categories.models import UserCategory
from src.common.enums import OperationType

class UserCategoryRepository(BaseRepository[UserCategory, CategoryUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=UserCategory, session=session)

    async def create(
            self,
            category_data: CategoryCreate,
            user_id: uuid.UUID
    ) -> UserCategory | None:
        data_dict = category_data.model_dump()
        existing_category = await self.get_by_name_and_type(
            category_data.name,
            category_data.type,
            user_id=user_id,
            only_active=False
        )

        if not existing_category:
            category = UserCategory(**data_dict, user_id=user_id)
            self.session.add(category)
        else:
            category = existing_category
            category.is_active = True

            for key, value in data_dict.items():
                setattr(category, key, value)

        await self.session.commit()
        await self.session.refresh(category)
        return category
    
    async def get_all_by_type(
            self,
            category_type: OperationType,
            user_id: uuid.UUID,
            only_active: bool = True
    ) -> list[UserCategory]:
        query = select(UserCategory).where(
            UserCategory.user_id == user_id,
            UserCategory.type == category_type
        )

        if only_active:
            query = self._get_active(query)

        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_name_and_type(
            self,
            category_name: str,
            category_type: OperationType,
            user_id: uuid.UUID,
            only_active: bool = True
    ) -> UserCategory | None:
        query = select(UserCategory).where(
            UserCategory.user_id == user_id,
            UserCategory.name == category_name,
            UserCategory.type == category_type
        )

        if only_active:
            query = self._get_active(query)

        result = await self.session.execute(query)
        return result.scalars().one_or_none()
    
    async def get_soft_deleted(
            self,
            category_name: str,
            category_type: OperationType,
            user_id: uuid.UUID
    ) -> UserCategory | None:
        query = select(UserCategory).where(
            UserCategory.user_id == user_id,
            UserCategory.name == category_name,
            UserCategory.type == category_type,
            UserCategory.is_active.is_(False)
        )

        result = await self.session.scalars(query)
        return result.one_or_none()
