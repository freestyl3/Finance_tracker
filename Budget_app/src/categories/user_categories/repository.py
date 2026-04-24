import uuid
from typing import override

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Sequence
from sqlalchemy.dialects.postgresql import insert

from src.core.repository.scoped import UserScopedRepository
from src.core.enums import RepoAction
from src.categories.user_categories.exceptions import (
    UserCategoryAlreadyExistsError, UserCategoryNotFoundError
)
from src.categories.user_categories.models import UserCategory
from src.categories.system_categories.models import SystemCategory

class UserCategoryRepository(UserScopedRepository[UserCategory]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserCategory, session)

    @override
    def _map_integrity_error(self, repo_action: RepoAction) -> Exception:
        if repo_action == RepoAction.CREATE:
            return UserCategoryAlreadyExistsError()
        elif repo_action == RepoAction.UPDATE:
            return UserCategoryAlreadyExistsError()
        return super()._map_integrity_error(repo_action)
    
    @override
    def _not_found(self) -> Exception:
        return UserCategoryNotFoundError()

    @override
    async def create(
        self,
        create_data: dict,
        user_id: uuid.UUID
    ) -> UserCategory | None:
        update_dict = {"is_active": True}

        data_to_insert = {**create_data, "user_id": user_id}

        query = (
            insert(UserCategory)
            .values(**data_to_insert)
            .on_conflict_do_update(
                constraint="uq_user_categories_name_user_type",
                set_=update_dict,
                where=(UserCategory.is_active.is_(False))
            )
            .returning(UserCategory)
        )        

        result = await self.session.execute(query)
        return result.scalars().one_or_none()
    
    async def batch_create(
            self,
            create_data: list[dict],
            user_id: uuid.UUID
    ) -> Sequence[UserCategory]:
        values_to_insert = [
            {
                **data,
                "user_id": user_id
            } for data in create_data
        ]

        stmt = (
            insert(UserCategory)
            .values(values_to_insert)
            .on_conflict_do_update(
                constraint="uq_user_categories_name_user_type",
                set_={"is_active": True},
                where=(UserCategory.is_active.is_(False))
            )
            .returning(UserCategory)
        )

        result = await self.session.scalars(stmt)
        return result.all()
    
    # Возможно стоит перенести в SystemCategoryRepository
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
