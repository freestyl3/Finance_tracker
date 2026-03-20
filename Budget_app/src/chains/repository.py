import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from src.chains.schemas import ChainCreate
from src.chains.models import Chain
from src.operations.models import Operation

class ChainRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _get_computed_fields_query(self, user_id: uuid.UUID):
        return (
            select(
                Operation.chain_id,
                func.count(Operation.id).label("operations_count"),
                func.sum(Operation.amount).label("operations_sum")
            )
            .where(
                Operation.user_id == user_id,
                Operation.chain_id.is_not(None)
            )
            .group_by(Operation.chain_id)
            .subquery()
        )

    async def create(
            self,
            chain_data: ChainCreate,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Chain:
        chain = Chain(
            **chain_data.model_dump(exclude=["operation_uuids",]),
            account_id=account_id,
            user_id=user_id
        )

        self.session.add(chain)
        await self.session.flush()

        return chain
    
    async def get_all(
            self,
            user_id: uuid.UUID
    ) -> list[Chain]:
        stats_stmt = self._get_computed_fields_query(user_id)

        query = (
            select(
                Chain,
                stats_stmt.c.operations_count,
                stats_stmt.c.operations_sum
            )
            .join(stats_stmt, Chain.id == stats_stmt.c.chain_id)
            .where(Chain.user_id == user_id)
        )

        result = await self.session.execute(query)
        
        chains = []
        for chain_obj, ops_count, ops_sum in result.unique():
            chain_obj.operations_count = ops_count
            chain_obj.amount = ops_sum
            chains.append(chain_obj)

        return chains
    
    async def get_by_id(
            self,
            chain_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Chain | None:
        stats_stmt = self._get_computed_fields_query(user_id)

        query = (
            select(
                Chain,
                stats_stmt.c.operations_count,
                stats_stmt.c.operations_sum
            )
            .join(stats_stmt, Chain.id == stats_stmt.c.chain_id)
            .where(Chain.id == chain_id, Chain.user_id == user_id)
        )

        result = await self.session.execute(query)
        row = result.unique().one_or_none()

        if row:
            chain_obj, operations_count, operations_sum = row
            chain_obj.operations_count = operations_count
            chain_obj.amount = operations_sum
            return chain_obj
        return None
    
    async def delete(
            self,
            chain_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool:
        query = delete(Chain).where(
            Chain.id == chain_id,
            Chain.user_id == user_id
        )

        result = await self.session.execute(query)
        await self.session.commit()

        return result.rowcount > 0
