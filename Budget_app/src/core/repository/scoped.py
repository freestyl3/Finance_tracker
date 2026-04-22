import uuid
from typing import override

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Sequence

from src.core.repository.base import BaseRepository, ModelType

class UserScopedRepository(BaseRepository[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        super().__init__(model, session)

    @override
    async def create(self, create_data: dict, user_id: uuid.UUID) -> ModelType:
        data_with_user = {**create_data, "user_id": user_id}
        return await super().create(data_with_user)
    
    @override
    async def batch_create(
            self,
            create_data_list: list[dict],
            user_id: uuid.UUID
    ) -> Sequence[ModelType]:
        data_with_user = [
            {**create_data, "user_id": user_id}
            for create_data in create_data_list
        ]
        return await super().batch_create(data_with_user)

    @override
    async def get_one_by(
            self,
            user_id: uuid.UUID,
            unique: bool = False,
            *load_options,
            **fields
    ) -> ModelType | None:
        fields["user_id"] = user_id
        return await super().get_one_by(unique, *load_options, **fields)

    @override
    async def get_all_by(
            self,
            user_id: uuid.UUID,
            unique: bool = False,
            *load_options,
            **fields
    ) -> Sequence[ModelType]:
        fields["user_id"] = user_id
        return await super().get_all_by(unique, *load_options, **fields)

    @override
    async def exists_by(
            self,
            user_id: uuid.UUID,
            **filters
    ) -> bool:
        filters["user_id"] = user_id
        return await super().exists_by(**filters)

    @override
    async def update(
            self,
            model_id: uuid.UUID,
            update_data: dict,
            user_id: uuid.UUID,
            raise_if_not_found: bool = False,
            **filters
    ) -> ModelType | None:
        filters["user_id"] = user_id
        return await super().update(
            model_id,
            update_data,
            raise_if_not_found,
            **filters
        )

    @override
    async def batch_update(
            self,
            values_by_id: dict[uuid.UUID, dict],
            user_id: uuid.UUID,
            **filters
    ) -> Sequence[ModelType]:
        filters["user_id"] = user_id
        return await super().batch_update(values_by_id, **filters)

    @override
    async def delete(
            self,
            model_id: uuid.UUID,
            user_id: uuid.UUID,
            raise_if_not_found: bool = False,
            **fields
    ) -> ModelType | None:
        fields["user_id"] = user_id
        return await super().delete(model_id, raise_if_not_found, **fields)
