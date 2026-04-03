import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, update
from sqlalchemy.orm import joinedload

from src.operations.models import Operation

class OperationChainRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

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
    ) -> bool:
        query = delete(Operation).where(
            Operation.chain_id == chain_id,
            Operation.user_id == user_id            
        )

        result = await self.session.execute(query)
        return result.rowcount > 0
    
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
