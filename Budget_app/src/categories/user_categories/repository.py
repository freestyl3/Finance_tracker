import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, Sequence
from sqlalchemy.dialects.postgresql import insert

from src.base.repository import ActiveNamedRepository
from src.categories.user_categories.models import UserCategory
from src.categories.system_categories.models import SystemCategory
from src.common.enums import OperationType
from src.operations.models import Operation

class UserCategoryRepository(ActiveNamedRepository[UserCategory]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=UserCategory, session=session)

    async def create(self, create_data: dict) -> UserCategory:
        update_dict = {"is_active": True}

        stmt = (
            insert(UserCategory)
            .values(**create_data)
            .on_conflict_do_update(
                constraint="uq_user_categories_name_user_type",
                set_=update_dict,
                where=(UserCategory.is_active.is_(False))
            )
            .returning(UserCategory)
        )        

        result = await self.session.scalars(stmt)
        await self.session.flush()

        return result.one_or_none()
    
    async def batch_create(self, create_data: list[dict]) -> Sequence[UserCategory]:
        stmt = (
            insert(UserCategory)
            .values(create_data)
            .on_conflict_do_update(
                constraint="uq_user_categories_name_user_type",
                set_={"is_active": True},
                where=(UserCategory.is_active.is_(False))
            )
            .returning(UserCategory)
        )

        result = await self.session.scalars(stmt)
        await self.session.flush()

        return result.all()
    
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
            query = query.where(UserCategory.is_active.is_(True))

        result = await self.session.execute(query)
        return result.scalars().unique().one_or_none()
    
    async def get_available_for_user(
            self,
            user_id: uuid.UUID
    ) -> Sequence[SystemCategory]:
        user_has_category = select(UserCategory).where(
            UserCategory.name == SystemCategory.name,
            UserCategory.type == SystemCategory.type,
            UserCategory.user_id == user_id,
            UserCategory.is_active.is_(True)
        ).exists()

        query = select(SystemCategory).where(~user_has_category)

        result = await self.session.scalars(query)
        return result.all()

    async def delete(
            self,
            category_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool:
        query = select(exists().where(Operation.category_id == category_id))
        result = await self.session.scalar(query)

        if result:
            return await self.soft_delete(category_id, user_id)
        return await super().delete(category_id, user_id)
        
    # async def get_all_by_type(
    #         self,
    #         category_type: OperationType,
    #         user_id: uuid.UUID,
    #         only_active: bool = True
    # ) -> list[UserCategory]:
    #     query = select(UserCategory).where(
    #         UserCategory.user_id == user_id,
    #         UserCategory.type == category_type
    #     )

    #     if only_active:
    #         query = self._get_active(query)

    #     result = await self.session.execute(query)
    #     return list(result.scalars().all())
    
    # async def get_soft_deleted(
    #         self,
    #         category_name: str,
    #         category_type: OperationType,
    #         user_id: uuid.UUID
    # ) -> UserCategory | None:
    #     query = select(UserCategory).where(
    #         UserCategory.user_id == user_id,
    #         UserCategory.name == category_name,
    #         UserCategory.type == category_type,
    #         UserCategory.is_active.is_(False)
    #     )

    #     result = await self.session.scalars(query)
    #     return result.one_or_none()
