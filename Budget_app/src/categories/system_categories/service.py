import uuid

from sqlalchemy.exc import IntegrityError

from src.core.uow import IUnitOfWork
from src.categories.system_categories.repository import SystemCategoryRepository
from src.categories.system_categories.schemas import SystemCategoryUpdate
from src.categories.base.schemas import CategoryCreate
from src.categories.system_categories.models import SystemCategory
from src.common.enums import OperationType

class SystemCategoryService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    @property
    def sys_cat_repo(self) -> SystemCategoryRepository:
        return self.uow.get_repo(SystemCategoryRepository)

    async def create(
            self,
            category_create: CategoryCreate
    ) -> SystemCategory:
        return await self.sys_cat_repo.create(
            create_data=category_create.model_dump()
        )
        
    async def get_all(self) -> list[SystemCategory]:
        return list(await self.sys_cat_repo.get_all_by())
    
    async def get_all_by_type(
            self,
            type: OperationType
    ) -> list[SystemCategory]:
        return await list(self.sys_cat_repo.get_all_by(type=type))
    
    async def get_by_id(self, category_id: uuid.UUID) -> SystemCategory | None:
        return await self.sys_cat_repo.get_one_by(id=category_id)
    
    async def update(
            self,
            category_id: uuid.UUID,
            category_update: SystemCategoryUpdate
    ) -> SystemCategory:
        return await self.sys_cat_repo.update(
            model_id=category_id,
            update_data=category_update.model_dump(exclude_unset=True),
            raise_if_not_found=True
        )
    
    async def delete(self, category_id: uuid.UUID) -> bool:
        return await self.sys_cat_repo.delete(
            model_id=category_id,
            raise_if_not_found=True
        )
