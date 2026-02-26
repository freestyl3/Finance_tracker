import uuid
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    def _get_active(self, query: Select) -> Select:
        if hasattr(self.model, "is_active"):
            return query.where(self.model.is_active.is_)
        return query

    async def get_by_id(
            self,
            model_id: uuid.UUID,
            user_id: uuid.UUID,
            only_active: bool = True
    ) -> ModelType | None:
        query = select(self.model).where(
            self.model.id == model_id,
            self.model.user_id == user_id
        )

        if only_active:
            query = self._get_active(query)

        result = await self.session.scalars(query)
        return result.one_or_none()
    
    async def get_by_name(
            self,
            model_name: str,
            user_id: uuid.UUID,
            only_active: bool = True
    ) -> ModelType | None:
        query = select(self.model).where(
            self.model.name == model_name,
            self.model.user_id == user_id
        )

        if only_active:
            query = self._get_active(query)

        result = await self.session.scalars(query)
        return result.one_or_none()
    
    ## Поменять на Sequence
    async def get_all(
            self,
            user_id: uuid.UUID,
            only_active: bool = True
    ) -> list[ModelType]:
        query = select(self.model).where(
            self.model.user_id == user_id
        )

        if only_active:
            query = self._get_active(query)

        result = await self.session.scalars(query)
        return list(result.all())
    
    async def update(
            self,
            model_id: uuid.UUID,
            update_data: UpdateSchemaType,
            user_id: uuid.UUID
    ) -> ModelType | None:
        obj = await self.get_by_id(model_id, user_id, only_active=True)

        if not obj:
            return None
        
        data = update_data.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(obj, key, value)

        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def soft_delete(
            self,
            model_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool:
        obj = await self.get_by_id(model_id, user_id, only_active=True)

        if obj:
            obj.is_active = False

            await self.session.commit()
            await self.session.refresh(obj)
            return True
        return False
