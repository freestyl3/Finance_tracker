import uuid
from typing import Generic, TypeVar

from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Sequence, delete, update
from sqlalchemy.orm.strategy_options import Load
# from pydantic import BaseModel

ModelType = TypeVar("ModelType")
# CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, create_data: dict, user_id: uuid.UUID) -> ModelType:
        obj = self.model(**create_data, user_id=user_id)

        self.session.add(obj)
        return obj

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
            user_id: uuid.UUID,
            *load_options: Load
    ) -> ModelType | None:
        query = select(self.model).where(
            self.model.id == model_id,
            self.model.user_id == user_id
        )

        if load_options:
            query = query.options(*load_options)

        result = await self.session.scalars(query)
        return result.unique().one_or_none()
    
    async def get_all(
            self,
            user_id: uuid.UUID,
            *load_options: Load
    ) -> Sequence[ModelType]:
        query = select(self.model).where(self.model.user_id == user_id)

        if load_options:
            query = query.options(*load_options)

        result = await self.session.scalars(query)
        return result.unique().all()
    
    async def update(
            self,
            model_id: uuid.UUID,
            update_data: dict,
            user_id: uuid.UUID
    ) -> ModelType | None:
        query = update(self.model).where(
            self.model.id == model_id,
            self.model.user_id == user_id
        ).values(
            **update_data
        ).returning(self.model)

        result = await self.session.scalars(query)
        return result.unique().one_or_none()
    
    async def delete(self, model_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        query = delete(self.model).where(
            self.model.id == model_id,
            self.model.user_id == user_id
        )
        
        result = await self.session.execute(query)

        return result.rowcount > 0


class ActiveNamedRepository(BaseRepository[ModelType]):
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
    ) -> bool | None:
        query = (
            update(self.model)
            .where(
                self.model.id == model_id,
                self.model.user_id == user_id,
                self.model.is_active.is_(True)
            )
            .values(is_active=False)
            .returning(self.model)
        )

        result = await self.session.execute(query)
        
        return result.scalars().one_or_none()
