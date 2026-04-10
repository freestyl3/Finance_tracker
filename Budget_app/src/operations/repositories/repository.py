import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select, update, not_, Sequence, delete, or_
from sqlalchemy.orm import joinedload, selectinload

from src.base.repository import BaseRepository
from src.operations.models import Operation
from src.operations.filters import OperationFilter
from src.pagination import PaginationParams
from src.categories.user_categories.models import UserCategory

class OperationRepository(BaseRepository[Operation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Operation, session)

    def _apply_report_filters(
            self,
            query: Select,
            filters: OperationFilter
    ) -> Select:
        if filters:
            if filters.categories:
                query = query.where(Operation.category_id.in_(filters.categories))
            if filters.accounts:
                query = query.where(Operation.account_id.in_(filters.accounts))
            if filters.type:
                query = (
                    query.join(UserCategory, Operation.category_id == UserCategory.id)
                    .where(UserCategory.type == filters.type)
                )
            if filters.date_from:
                query = query.where(Operation.date >= filters.date_from)
            if filters.date_to:
                query = query.where(Operation.date <= filters.date_to)
        return query

    async def get_all(
            self,
            user_id: uuid.UUID,
            filter_params: OperationFilter,
            pagination: PaginationParams
    ) -> Sequence[Operation]:
        query = (
            select(Operation)
            .options(
                joinedload(Operation.category), joinedload(Operation.account)
            )
            .where(Operation.user_id == user_id)
        )
        query = self._apply_report_filters(query, filter_params)
        query = query.order_by(Operation.date.desc())
        query = query.limit(pagination.limit).offset(pagination.offset)

        result = await self.session.execute(query)
        return result.scalars().unique().all()
    
    async def change_visibility(
            self,
            operation_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Operation | None:
        query = (
            update(Operation)
            .options(
                selectinload(Operation.category),
                selectinload(Operation.account)
            )
            .where(
                Operation.id == operation_id,
                Operation.user_id == user_id,
                Operation.chain_id.is_(None)
            )
            .values(ignore=not_(Operation.ignore))
            .returning(Operation)
        )

        result = await self.session.scalars(query)
        await self.session.commit()
        return result.unique().one_or_none()

    async def delete(
            self,
            operation_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Sequence[Operation]:
        query = (
            delete(Operation)
            .where(
                Operation.user_id == user_id,
                or_(
                    Operation.id == operation_id,
                    Operation.related_operation_id == operation_id
                )
            )
            .returning(Operation)
        )

        result = await self.session.execute(query)
        return result.scalars().unique().all()

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