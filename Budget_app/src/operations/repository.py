import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select, delete
from sqlalchemy.orm import joinedload

from src.base.repository import BaseRepository
from src.operations.models import Operation
from src.base.filters import OperationFilterBase
from src.operations.schemas import OperationCreate, OperationUpdate
from src.pagination import PaginationParams

class OperationRepository(BaseRepository[Operation, OperationUpdate]):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _apply_report_filters(
            self,
            query: Select,
            filters: OperationFilterBase
    ) -> Select:
        if filters.category_id:
            query = query.where(Operation.category_id == filters.category_id)
        if filters.date_from:
            query = query.where(Operation.date >= filters.date_from)
        if filters.date_to:
            query = query.where(Operation.date <= filters.date_to)
        return query
    
    async def create(
            self,
            operation_data: OperationCreate,
            user_id: int
    ) -> Operation:
        operation = Operation(**operation_data.model_dump(), user_id=user_id)
        
        self.session.add(operation)
        await self.session.commit()
        await self.session.refresh(operation)

        return operation

    async def get_all(
            self,
            user_id: uuid.UUID,
            filter_params: OperationFilterBase,
            pagination: PaginationParams
    ) -> list[Operation]:
        query = (
            select(Operation)
            .options(
                joinedload(Operation.category), joinedload(Operation.account)
            )
            .where(Operation.account.user_id == user_id)
        )
        query = self._apply_report_filters(query, filter_params)
        query = query.order_by(Operation.date.desc())
        query = query.limit(pagination.limit).offset(pagination.offset)

        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    # async def get_by_id(
    #         self,
    #         operation_id: uuid.UUID,
    #         user_id: uuid.UUID
    # ) -> Operation | None:
    #     query = select(Operation).where(
    #         Operation.id == operation_id,
    #         Operation.user_id == user_id
    #     )
    #     result = await self.session.execute(query)
    #     return result.scalars().one_or_none()
    
    # async def delete(self, operation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    #     query = delete(Operation).where(
    #         Operation.id == operation_id,
    #         Operation.user_id == user_id
    #     )
    #     result = await self.session.execute(query)
    #     await self.session.commit()

    #     return result.rowcount > 0
    
    # async def update(
    #         self,
    #         operation_id: uuid.UUID,
    #         operation_update: OperationUpdate,
    #         user_id: uuid.UUID
    # ) -> Operation | None:
    #     operation = await self.get_by_id(operation_id, user_id)

    #     if not operation:
    #         return None
        
    #     update_data = operation_update.model_dump(exclude_unset=True)

    #     for key, value in update_data.items():
    #         setattr(operation, key, value)

    #     await self.session.commit()
    #     await self.session.refresh(operation)

    #     return operation
    
    # async def get_total_amount(
    #         self,
    #         user_id: int,
    #         filters: ReportFilter
    # ) -> float:
    #     query = select(
    #         func.sum(Operation.amount).label("total")
    #     ).where(Operation.user_id == user_id)

    #     query = self._apply_report_filters(query, filters)
    #     result = await self.session.execute(query)

    #     return result.scalar() or 0.0
    
    # async def get_operations_stats(
    #         self,
    #         user_id: int,
    #         filter_params: ReportFilter
    # ) -> dict:
    #     total_amount = func.sum(Operation.amount).label("total_amount")

    #     query = (
    #         select(
    #             Operation.category_id,
    #             self.category.name.label("category_name"),
    #             total_amount
    #         )
    #         .join(self.category, Operation.category_id == self.category.id)
    #         .where(Operation.user_id == user_id)
    #         .group_by(Operation.category_id, self.category.name)
    #         .order_by(total_amount.desc())
    #     )

    #     query = self._apply_report_filters(query, filter_params)

    #     grouped_result = await self.session.execute(query)
    #     total_sum = await self.get_total_amount(user_id, filter_params)

    #     return {
    #         "total_sum": total_sum,
    #         "categories": grouped_result.mappings().all()
    #     }