import uuid

from fastapi import HTTPException, status, Response

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
            new_category = await self.repo.create(category_create)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        return new_category

    
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
        updated = await self.repo.update(category_id, category_update)

        if not updated:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="System category not found"
            )
        
        return updated
    
    async def delete(self, category_id: uuid.UUID) -> bool:
        await self.repo.delete(category_id)

        return Response(status_code=status.HTTP_204_NO_CONTENT)
