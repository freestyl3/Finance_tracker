from abc import ABC
from typing import Generic, TypeVar

from sqlalchemy import select, delete, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import AbstractOperation, CategoryBase
from src.reports.schemas import ReportFilter
from src.pagination import PaginationParams
from src.base.filters import OperationFilterBase
from src.base.schemas import OperationCreate, OperationUpdate

ModelType = TypeVar("ModelType", bound=AbstractOperation)

class BaseOperationRepository(ABC, Generic[ModelType]):
    def __init__(
            self,
            session: AsyncSession,
            operation_model: type[ModelType],
            operation_category: type[CategoryBase]
    ):
        self.session = session
        self.model = operation_model
        self.category = operation_category

    def _apply_report_filters(self, query, filters: OperationFilterBase):
        if filters.category_id:
            query = query.where(self.model.category_id == filters.category_id)
        if filters.date_from:
            query = query.where(self.model.date >= filters.date_from)
        if filters.date_to:
            query = query.where(self.model.date <= filters.date_to)
        return query
    
    async def _check_category_owner(
            self,
            category_id: int,
            user_id: int
    ) -> bool:
        query = select(self.category.id).where(
            self.category.id == category_id,
            self.category.user_id == user_id
        )

        result = await self.session.execute(query)
        return result.scalars().one_or_none() is not None
    
    async def create(
            self,
            operation_data: OperationCreate,
            user_id: int
    ) -> AbstractOperation:
        operation = self.model(**operation_data.model_dump(), user_id=user_id)

        if not await self._check_category_owner(
            operation.category_id,
            user_id
        ):
            raise ValueError("Not valid category.")
        
        self.session.add(operation)
        await self.session.commit()
        await self.session.refresh(operation)
        return operation

    async def get_operations(
            self,
            user_id: int,
            filter_params: OperationFilterBase,
            pagination: PaginationParams
    ) -> list[AbstractOperation]:
        query = (
            select(self.model)
            .options(joinedload(self.model.category))
            .where(self.model.user_id == user_id)
        )
        query = self._apply_report_filters(query, filter_params)
        query = query.order_by(self.model.date.desc())
        query = query.limit(pagination.limit).offset(pagination.offset)

        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_total_amount(
            self,
            user_id: int,
            filters: ReportFilter
    ) -> float:
        query = select(
            func.sum(self.model.amount).label("total")
        ).where(self.model.user_id == user_id)

        query = self._apply_report_filters(query, filters)
        result = await self.session.execute(query)

        return result.scalar() or 0.0
    
    async def get_operations_stats(
            self,
            user_id: int,
            filter_params: ReportFilter
    ) -> dict:
        total_amount = func.sum(self.model.amount).label("total_amount")

        query = (
            select(
                self.model.category_id,
                self.category.name.label("category_name"),
                total_amount
            )
            .join(self.category, self.model.category_id == self.category.id)
            .where(self.model.user_id == user_id)
            .group_by(self.model.category_id, self.category.name)
            .order_by(total_amount.desc())
        )

        query = self._apply_report_filters(query, filter_params)

        grouped_result = await self.session.execute(query)
        total_sum = await self.get_total_amount(user_id, filter_params)

        return {
            "total_sum": total_sum,
            "categories": grouped_result.mappings().all()
        }
    
    async def get_operation_by_id(
            self,
            operation_id: int,
            user_id: int
    ) -> AbstractOperation | None:
        query = select(self.model).where(
            self.model.id == operation_id,
            self.model.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()
    
    async def delete_operation(self, operation_id: int, user_id: int) -> bool:
        query = delete(self.model).where(
            self.model.id == operation_id,
            self.model.user_id == user_id
        )
        result = await self.session.execute(query)
        await self.session.commit()

        return result.rowcount > 0
    
    async def update_operation(
            self,
            operation_id: int,
            user_id: int,
            operation_update: OperationUpdate
    ) -> AbstractOperation | None:
        operation = await self.get_operation_by_id(operation_id, user_id)

        if not operation:
            return None
        
        update_data = operation_update.model_dump(exclude_unset=True)

        if update_data.get("category_id", None):
            if not await self._check_category_owner(
                update_data["category_id"],
                user_id
            ):
                raise ValueError("Not valid category.")

        for key, value in update_data.items():
            setattr(operation, key, value)

        await self.session.commit()
        await self.session.refresh(operation)

        return operation
