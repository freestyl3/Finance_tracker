import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.categories.base.schemas import CategoryCreate, CategoryUpdate
from src.categories.user_categories.models import UserCategory
### Temporary import
from src.operations.models import OperationType

class UserCategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
            self,
            category_data: CategoryCreate,
            user_id: uuid.UUID
    ) -> UserCategory:
        data_dict = category_data.model_dump()
        existing_category = await self.get_by_name_and_type(
            category_data.name,
            category_data.type,
            user_id=user_id
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
    
    async def get_all_active(self, user_id: uuid.UUID) -> list[UserCategory]:
        query = select(UserCategory).where(
            UserCategory.user_id == user_id,
            UserCategory.is_active == True
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_all_active_by_type(
            self,
            category_type: OperationType,
            user_id: uuid.UUID
    ) -> list[UserCategory]:
        query = select(UserCategory).where(
            UserCategory.user_id == user_id,
            UserCategory.type == category_type,
            UserCategory.is_active == True
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_active_by_id(
            self,
            category_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> UserCategory | None:
        query = select(UserCategory).where(
            UserCategory.user_id == user_id,
            UserCategory.id == category_id,
            UserCategory.is_active == True
        )

        result = await self.session.execute(query)
        return result.scalars().one_or_none()
    
    async def get_by_name_and_type(
            self,
            category_name: str,
            category_type: OperationType,
            user_id: uuid.UUID
    ) -> UserCategory | None:
        query = select(UserCategory).where(
            UserCategory.user_id == user_id,
            UserCategory.name == category_name,
            UserCategory.type == category_type
        )

        result = await self.session.execute(query)
        return result.scalars().one_or_none()
    
    async def update(
            self,
            category_id: uuid.UUID,
            category_data: CategoryUpdate,
            user_id: uuid.UUID
    ) -> UserCategory | None:
        category = await self.get_active_by_id(category_id, user_id)

        if not category:
            return None
        
        update_data = category_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(category, key, value)

        await self.session.commit()
        await self.session.refresh(category)
        return category
    
    async def soft_delete(
            self,
            category_id: uuid.UUID,
            user_id: uuid.UUID
        ) -> bool:
            category = await self.get_active_by_id(category_id, user_id)

            if category:
                category.is_active = False

                await self.session.commit()
                await self.session.refresh(category)
                return True
            return False
