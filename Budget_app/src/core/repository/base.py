from typing import Generic, TypeVar
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, Sequence
from sqlalchemy import case

from src.database.base import Base
from src.core.enums import RepoAction

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    def _map_integrity_error(self, repo_action: RepoAction) -> Exception:
        return RuntimeError(f"Integrity error during {repo_action}")
    
    def _not_found(self) -> Exception:
        return RuntimeError(f"{self.model.__name__} not found")
    
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
        
    async def create(self, create_data: dict, **kwargs) -> ModelType:
        obj = self.model(**create_data)
        self.session.add(obj)
        await self._flush_orm(RepoAction.CREATE)
        return obj
    
    async def batch_create(
            self,
            create_data_list: list[dict],
            **kwargs
    ) -> Sequence[ModelType]:
        operations =[self.model(**data) for data in create_data_list]

        self.session.add_all(operations)
        await self._flush_orm(RepoAction.CREATE)
        
        return operations

    async def get_one_by(
            self,
            unique: bool = False,
            *load_options,
            **fields
    ) -> ModelType | None:
        query = self._prepare_select_query(*load_options, **fields)

        result = await self.session.scalars(query)

        if unique:
            result = result.unique()
        
        return result.one_or_none()
    
    async def get_all_by(
            self,
            unique: bool = False,
            *load_options,
            **fields
    ) -> Sequence[ModelType]:
        query = self._prepare_select_query(*load_options, **fields)

        result = await self.session.scalars(query)

        if unique:
            result = result.unique()

        return result.all()
    
    async def exists_by(
            self,
            **filters
    ) -> bool:
        base_query = self._prepare_select_query(**filters)
    
        query = select(base_query.exists())
        
        result = await self.session.execute(query)
        return bool(result.scalar())
    
    async def update(
            self,
            model_id: uuid.UUID,
            update_data: dict,
            raise_if_not_found: bool = False,
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
        updated = result.scalars().one_or_none()

        if raise_if_not_found and updated is None:
            raise self._not_found()

        return updated
    
    async def batch_update(
            self,
            values_by_id: dict[uuid.UUID, dict],
            **filters
    ) -> Sequence[ModelType]:
        if not values_by_id:
            return []

        fields = set()
        for values in values_by_id.values():
            fields.update(values.keys())

        update_values = {}

        for field in fields:
            if not hasattr(self.model, field):
                raise ValueError(f"Model {self.model.__name__} doesn't have field '{field}'")
                
            column = getattr(self.model, field)

            case_dict = {
                obj_id: field_values[field]
                for obj_id, field_values in values_by_id.items()
                if field in field_values
            }

            update_values[field] = case(case_dict, value=self.model.id, else_=column)

        query = (
            update(self.model)
            .where(self.model.id.in_(values_by_id.keys()))
            .values(**update_values)
            .returning(self.model)
        )

        for key, value in filters.items():
            if not hasattr(self.model, key):
                raise ValueError(f"Model {self.model.__name__} doesn't have field '{key}'")

            query = query.where(getattr(self.model, key) == value)

        result = await self._execute(query, RepoAction.UPDATE)
        return result.scalars().all()

    async def delete(
            self,
            model_id: uuid.UUID,
            raise_if_not_found: bool = False,
            **fields
    ) -> ModelType | None:
        query = (
            delete(self.model)
            .where(self.model.id == model_id)
            .returning(self.model)
        )

        for key, value in fields.items():
            if not hasattr(self.model, key):
                raise ValueError(f"Model {self.model.__name__} doesn't have field {key}")
            
            query = query.where(getattr(self.model, key) == value)

        result = await self._execute(query, RepoAction.DELETE)
        deleted = result.scalar_one_or_none()

        if raise_if_not_found and deleted is None:
            raise self._not_found()

        return deleted
