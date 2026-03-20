import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select, delete, func, update, not_, or_
from sqlalchemy.orm import joinedload, selectinload

from src.base.repository import BaseRepository
from src.operations.models import Operation
from src.operations.filters import OperationFilter
from src.operations.schemas import OperationCreate, OperationUpdate
from src.pagination import PaginationParams
from src.categories.user_categories.models import UserCategory

class OperationRepository(BaseRepository[Operation, OperationUpdate]):
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
            filter_params: OperationFilter,
            pagination: PaginationParams
    ) -> list[Operation]:
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
        return list(result.scalars().unique().all())
    
    async def update(
            self,
            operation: Operation,
            update_data: OperationUpdate
    ) -> Operation:
        data = update_data.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(operation, key, value)

        await self.session.commit()
        await self.session.refresh(operation)

        return operation
    
    async def delete(
            self,
            operation: Operation
    ) -> bool:
        query = delete(Operation).where(
            Operation.id == operation.id
        )

        result = await self.session.execute(query)
        await self.session.commit()

        return result.rowcount > 0
    
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
    
    async def get_info_for_chain_validation(
            self,
            operation_uuids: list[uuid.UUID],
            user_id: uuid.UUID
    ):
        query = (
            select(
                Operation.account_id,
                UserCategory.type,
                func.count(Operation.id).over().label("found_count")
            )
            .join(UserCategory, Operation.category_id == UserCategory.id)
            .where(
                Operation.user_id == user_id,
                Operation.id.in_(operation_uuids),
                Operation.chain_id.is_(None)
            )
            .distinct()
        )

        result = await self.session.execute(query)
        return result.all()
    
    async def get_sum_of_operations(
            self,
            operation_uuids: list[uuid.UUID],
            user_id: uuid.UUID
        ) -> Decimal | None:
        query = select(func.sum(Operation.amount)).where(
            Operation.user_id == user_id,
            Operation.id.in_(operation_uuids)
        )

        result = await self.session.scalars(query)
        return result.unique().one_or_none()
    
    async def update_with_chain(
            self,
            operation_uuids: list[uuid.UUID],
            chain_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> list[Operation]:
        query = (
            update(Operation)
            .where(
                Operation.user_id == user_id,
                Operation.id.in_(operation_uuids)
            )
            .values(chain_id=chain_id, ignore=False)
            .returning(Operation)
        )

        result = await self.session.scalars(query)
        return result.unique().all()
    
    async def get_operations_for_chain(
            self,
            operation_ids: list[uuid.UUID],
            user_id: uuid.UUID,
            chain_id: uuid.UUID | None = None
    ) -> list[Operation]:
        query = (
            select(Operation)
            .options(
                joinedload(Operation.category),
                joinedload(Operation.account)
            )
            .where(
                Operation.user_id == user_id,
                Operation.id.in_(operation_ids)
            )
        )

        if not chain_id:
            query = query.where(Operation.chain_id.is_(None))
        else:
            query = query.where(
                or_(
                    Operation.chain_id.is_(None),
                    Operation.chain_id == chain_id
                )
            )

        result = await self.session.scalars(query)
        return result.unique().all()
    
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