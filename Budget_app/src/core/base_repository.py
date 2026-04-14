from typing import Generic, TypeVar
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete

from src.database.base import Base
from src.core.enums import RepoAction

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    def _map_integrity_error(self, repo_action: RepoAction) -> Exception:
        return RuntimeError(f"Integrity error during {repo_action}")
    
    def _prepare_select_query(self, *load_options, **fields):
        query = select(self.model)

        for key, value in fields.items():
            if not hasattr(self.model, key):
                raise ValueError(f"Model {self.model.__name__} doesn't have field {key}")
            
            query = query.where(getattr(self.model, key) == value)

        if load_options:
            query = query.options(*load_options)

        return query

    async def _flush_orm(self, repo_action: RepoAction):
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise self._map_integrity_error(repo_action) from e
        
    async def _execute(self, query, repo_action: RepoAction) -> AsyncResult:
        try:
            return await self.session.execute(query)
        except IntegrityError:
            raise self._map_integrity_error(repo_action)
        
    async def create(self, create_data) -> ModelType:
        obj = self.model(**create_data)
        self.session.add(obj)
        await self._flush_orm(RepoAction.CREATE)
        return obj

    async def get_one_by(self, *load_options, **fields) -> ModelType | None:
        query = self._prepare_select_query(*load_options, **fields)

        result = await self.session.scalars(query)
        return result.unique().one_or_none()
    
    async def get_all_by(self, *load_options, **fields) -> list[ModelType]:
        query = self._prepare_select_query(*load_options, **fields)

        result = await self.session.scalars(query)
        return result.unique().all()
    
    async def update(
            self,
            model_id: uuid.UUID,
            update_data: dict,
            **filters
    ) -> ModelType | None:
        query = (
            update(self.model)
            .where(self.model.id == model_id)
            .values(**update_data)
            .returning(self.model)
        )

        for key, value in filters.items():
            if not hasattr(self.model, key):
                raise ValueError(f"Model {self.model.__name__} doesn't have field {key}")
            
            query = query.where(getattr(self.model, key) == value)
        
        result = await self._execute(query, RepoAction.UPDATE)
        return result.scalars().unique().one_or_none()

    async def delete(self, model_id: uuid.UUID, **fields) -> bool:
        query = delete(self.model).where(self.model.id == model_id)

        for key, value in fields.items():
            if not hasattr(self.model, key):
                raise ValueError(f"Model {self.model.__name__} doesn't have field {key}")
            
            query = query.where(getattr(self.model, key) == value)

        result = await self._execute(query, RepoAction.DELETE)
        return result.rowcount > 0
