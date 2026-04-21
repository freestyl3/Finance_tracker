import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_, Select, Sequence
from sqlalchemy.orm import joinedload

from src.core.repository.scoped import UserScopedRepository
from src.operations.models import Operation
from src.operations.filters import OperationFilter
from src.pagination import PaginationParams
from src.categories.user_categories.models import UserCategory

class OperationRepository(UserScopedRepository[Operation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Operation, session)

    def _apply_report_filters(
            self,
            query: Select,
            filters: OperationFilter
    ) -> Select:
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
    
    # Методы бывшего OperationChainRepository
    def _base_query(
            self,
            user_id: uuid.UUID
    ):
        return (
            select(Operation)
            .options(
                joinedload(Operation.category),
                joinedload(Operation.account)
            )
            .where(
                Operation.user_id == user_id
            )
        )

    async def get_chains_operations(
        self,
        chain_ids: list[uuid.UUID] | None,
        user_id: uuid.UUID
    ) -> list[Operation]:
        if not chain_ids:
            return []

        query = self._base_query(user_id).where(
            Operation.chain_id.in_(chain_ids)
        )

        result = await self.session.scalars(query)
        return result.unique().all()
    
    async def get_operations_for_chain(
            self,
            operation_ids: list[uuid.UUID],
            user_id: uuid.UUID,
            chain_id: uuid.UUID | None = None,
            allow_free: bool = False
    ) -> list[Operation]:
        query = self._base_query(user_id).where(
            Operation.id.in_(operation_ids)
        )

        chain_conditions = []

        if allow_free:
            chain_conditions.append(Operation.chain_id.is_(None))

        if chain_id:
            chain_conditions.append(Operation.chain_id == chain_id)

        if chain_conditions:
            query = query.where(or_(*chain_conditions))
        else:
            return []

        result = await self.session.scalars(query)
        return result.unique().all()

    async def get_all_for_chain_update(self, user_id, chain_id, new_op_ids):
        query = self._base_query(user_id).where(
            or_(
                Operation.chain_id == chain_id,
                Operation.id.in_(new_op_ids)
            )
        )

        result = await self.session.execute(query)
        return result.scalars().unique().all()
    
    async def delete_chain_operations(
            self,
            chain_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> list[Operation]:
        query = (
            delete(Operation)
            .where(
                Operation.chain_id == chain_id,
                Operation.user_id == user_id            
            )
            .returning(Operation)
        )

        result = await self.session.scalars(query)
        return result.all()
    
    async def update_with_chain(
        self,
        operation_uuids: list[uuid.UUID],
        chain_id: uuid.UUID | None,
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
