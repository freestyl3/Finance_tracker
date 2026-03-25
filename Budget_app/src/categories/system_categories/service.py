import uuid

from sqlalchemy.exc import IntegrityError

from src.categories.system_categories.repository import SystemCategoryRepository
from src.categories.system_categories.schemas import SystemCategoryUpdate
from src.categories.base.schemas import CategoryCreate
from src.categories.system_categories.models import SystemCategory
from src.common.enums import OperationType

class SystemCategoryService:
    def __init__(self, repo: SystemCategoryRepository):
        self.repo = repo

    async def create(
            self,
            category_create: CategoryCreate
    ) -> SystemCategory:
        try:
            category = await self.repo.create(category_create)

            await self.repo.session.commit()
            await self.repo.session.refresh(category)

            return category
        except IntegrityError:
            raise ValueError("Duplicate system category in base!")
    
    async def get_all(self) -> list[SystemCategory]:
        return list(await self.repo.get_all())
    
    async def get_all_by_type(
            self,
            type: OperationType
    ) -> list[SystemCategory]:
        return await list(self.repo.get_all_by_type(type))
    
    async def get_by_id(self, category_id: uuid.UUID) -> SystemCategory | None:
        return await self.repo.get_by_id(category_id)
    
    async def update(
            self,
            category_id: uuid.UUID,
            category_update: SystemCategoryUpdate
    ) -> SystemCategory:
        try:
            updated = await self.repo.update(category_id, category_update)

            if not updated:
                await self.repo.session.rollback()
                raise ValueError("System category not found")

            await self.repo.session.commit()
            await self.repo.session.refresh(updated)

            return updated
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))
    
    async def delete(self, category_id: uuid.UUID) -> bool:
        result = await self.repo.delete(category_id)
        await self.repo.session.commit()

        return result
