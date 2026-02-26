import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.categories.system_categories.models import SystemCategory
from src.categories.base.schemas import CategoryCreate
from src.categories.system_categories.schemas import SystemCategoryUpdate
### Temporary import
from src.operations.models import OperationType

class SystemCategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, category_data: CategoryCreate) -> SystemCategory:
        category = SystemCategory(**category_data.model_dump())

        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def get_all(self) -> list[SystemCategory]:
        query = select(SystemCategory)

        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_all_by_type(self, type: OperationType) -> list[SystemCategory]:
        query = select(SystemCategory).where(SystemCategory.type == type)

        result = await self.session.execute(query)
        return list(result.scalars().all())
    
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
