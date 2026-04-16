import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Sequence, update

from src.core.base_repository import BaseRepository
from src.categories.system_categories.models import SystemCategory
from src.core.enums import RepoAction
from src.categories.system_categories.exceptions import (
    SystemCategoryAlreadyExistsError, SystemCategoryNotFoundError
)
from src.common.enums import OperationType

class SystemCategoryRepository(BaseRepository[SystemCategory]):
    def __init__(self, session: AsyncSession):
        super().__init__(SystemCategory, session)

    def _map_integrity_error(self, repo_action: RepoAction) -> Exception:
        if repo_action == RepoAction.CREATE:
            return SystemCategoryAlreadyExistsError()
        return super()._map_integrity_error(repo_action)
    
    def _not_found(self) -> Exception:
        return SystemCategoryNotFoundError()

    # async def create(self, category_data: CategoryCreate) -> SystemCategory:
    #     category = SystemCategory(**category_data.model_dump())

    #     self.session.add(category)
    #     return category

    # async def get_all(self) -> Sequence[SystemCategory]:
    #     query = select(SystemCategory)

    #     result = await self.session.execute(query)
    #     return result.scalars().all()
    
    # async def get_all_by_type(
    #         self,
    #         type: OperationType
    # ) -> Sequence[SystemCategory]:
    #     query = select(SystemCategory).where(SystemCategory.type == type)

    #     result = await self.session.execute(query)
    #     return result.scalars().all()
    
    # async def get_by_id(self, category_id: uuid.UUID) -> SystemCategory | None:
    #     query = select(SystemCategory).where(SystemCategory.id == category_id)

    #     result = await self.session.execute(query)
    #     return result.scalars().one_or_none()
    
    # async def update(
    #         self,
    #         category_id: uuid.UUID,
    #         category_data: SystemCategoryUpdate
    # ) -> SystemCategory | None:
    #     query = (
    #         update(SystemCategory)
    #         .where(SystemCategory.id == category_id)
    #         .values(**category_data.model_dump())
    #         .returning(SystemCategory)
    #     )

    #     result = await self.session.scalars(query)
    #     return result.unique().one_or_none()
    
    # async def delete(self, category_id: uuid.UUID) -> bool:
    #     query = delete(SystemCategory).where(SystemCategory.id == category_id)

    #     result = await self.session.execute(query)
    #     return result.rowcount > 0
