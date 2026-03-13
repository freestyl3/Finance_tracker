import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Sequence, and_

from src.categories.system_categories.models import SystemCategory
from src.categories.base.schemas import CategoryCreate
from src.categories.system_categories.schemas import SystemCategoryUpdate
from src.common.enums import OperationType
from src.categories.user_categories.models import UserCategory

class SystemCategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, category_data: CategoryCreate) -> SystemCategory:
        category = SystemCategory(**category_data.model_dump())

        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def get_all(self) -> Sequence[SystemCategory]:
        query = select(SystemCategory)

        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_all_by_type(
            self,
            type: OperationType
    ) -> Sequence[SystemCategory]:
        query = select(SystemCategory).where(SystemCategory.type == type)

        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_available_for_user(
            self,
            user_id: uuid.UUID
    ) -> Sequence[SystemCategory]:
        query = select(SystemCategory).outerjoin(
            UserCategory,
            and_(
                UserCategory.name == SystemCategory.name,
                UserCategory.type == SystemCategory.type,
                UserCategory.user_id == user_id,
                UserCategory.is_active.is_(True)
            )
        ).where(UserCategory.id.is_(None))

        result = await self.session.scalars(query)
        return result.all()
    
    async def get_by_id(self, category_id: uuid.UUID) -> SystemCategory | None:
        query = select(SystemCategory).where(SystemCategory.id == category_id)

        result = await self.session.execute(query)
        return result.scalars().one_or_none()
    
    async def update(
            self,
            category_id: uuid.UUID,
            category_data: SystemCategoryUpdate
    ) -> SystemCategory | None:
        category = await self.get_by_id(category_id)

        if not category:
            return None
        
        update_data = category_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(category, key, value)

        await self.session.commit()
        await self.session.refresh(category)
        return category
    
    async def delete(self, category_id: uuid.UUID) -> bool:
        query = delete(SystemCategory).where(SystemCategory.id == category_id)
        result = await self.session.execute(query)
        await self.session.commit()

        return result.rowcount > 0
