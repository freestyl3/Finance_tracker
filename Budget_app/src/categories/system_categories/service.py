import uuid

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
        return await self.repo.create(category_create)
    
    async def get_all(self) -> list[SystemCategory]:
        return await list(self.repo.get_all())
    
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
        return await self.repo.update(category_id, category_update)
    
    async def delete(self, category_id: uuid.UUID) -> bool:
        return await self.repo.delete(category_id)
