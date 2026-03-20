import uuid
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Sequence, delete, update
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_one_by(
        self, 
        user_id: uuid.UUID,
        **kwargs
    ) -> ModelType | None:
        query = select(self.model).where(self.model.user_id == user_id)

        for key, value in kwargs.items():
            if not hasattr(self.model, key):
                raise ValueError(f"Model {self.model.__name__} doesn't have field {key}")
            
            query = query.where(getattr(self.model, key) == value)

        result = await self.session.scalars(query)
        return result.unique().one_or_none()
    
    async def get_all_by(
        self, 
        user_id: uuid.UUID,
        **kwargs
    ) -> ModelType | None:
        query = select(self.model).where(self.model.user_id == user_id)

        for key, value in kwargs.items():
            if not hasattr(self.model, key):
                raise ValueError(f"Model {self.model.__name__} doesn't have field {key}")
            
            query = query.where(getattr(self.model, key) == value)

        result = await self.session.scalars(query)
        return result.unique().all()
    
    async def get_by_id(
            self,
            model_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> ModelType | None:
        query = select(self.model).where(
            self.model.id == model_id,
            self.model.user_id == user_id
        )

        result = await self.session.scalars(query)
        return result.unique().one_or_none()
    
    async def get_all(self, user_id: uuid.UUID) -> Sequence[ModelType]:
        query = select(self.model).where(self.model.user_id == user_id)

        result = await self.session.scalars(query)
        return result.unique().all()
    
    async def update(
            self,
            model_id: uuid.UUID,
            update_data: UpdateSchemaType,
            user_id: uuid.UUID
    ) -> ModelType | None:
        query = update(self.model).where(
            self.model.id == model_id,
            self.model.user_id == user_id
        ).values(
            **update_data.model_dump(exclude_unset=True)
        ).returning(self.model)

        result = await self.session.scalars(query)
        return result.unique().one_or_none()
    
    async def delete(self, model_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        query = delete(self.model).where(
            self.model.id == model_id,
            self.model.user_id == user_id
        )
        result = await self.session.execute(query)
        await self.session.commit()

        return result.rowcount > 0


class ActiveNamedRepository(BaseRepository[ModelType, UpdateSchemaType]):
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
            query = query.where(self.model.is_active.is_(True))

        result = await self.session.scalars(query)
        return result.unique().one_or_none()
    
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
            query = query.where(self.model.is_active.is_(True))

        result = await self.session.scalars(query)
        return result.unique().one_or_none()
    
    async def get_all(
            self,
            user_id: uuid.UUID,
            only_active: bool = True
    ) -> list[ModelType]:
        query = select(self.model).where(self.model.user_id == user_id)

        if only_active:
            query = query.where(self.model.is_active.is_(True))

        result = await self.session.scalars(query)
        return result.unique().all()

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