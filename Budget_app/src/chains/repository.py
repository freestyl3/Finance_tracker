import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, update
from sqlalchemy.orm import joinedload, selectinload

from src.chains.schemas import ChainCreate, ChainUpdate
from src.chains.models import Chain
from src.operations.models import Operation

class ChainRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _get_stats_subqueries(self):
        amount_subq = (
            select(func.sum(Operation.amount))
            .where(Operation.chain_id == Chain.id)
            .scalar_subquery()
        )
        count_subq = (
            select(func.count(Operation.id))
            .where(Operation.chain_id == Chain.id)
            .scalar_subquery()
        )
        return amount_subq, count_subq

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
    
    async def get_all(self, user_id: uuid.UUID) -> list[Chain]:
        amount_subq, count_subq = self._get_stats_subqueries()

        query = (
            select(
                Chain,
                amount_subq.label("computed_amount"),
                count_subq.label("computed_count")
            )
            .options(
                joinedload(Chain.account),
                joinedload(Chain.category)
            )
            .where(Chain.user_id == user_id)
            .order_by(Chain.date.desc())
        )

        result = await self.session.execute(query)
        
        chains = []
        for chain_obj, amount, count in result.unique():
            chain_obj.amount = amount or 0
            chain_obj.operations_count = count or 0
            chains.append(chain_obj)

        return chains

    async def get_by_id(self, chain_id: uuid.UUID, user_id: uuid.UUID) -> Chain | None:
        amount_subq, count_subq = self._get_stats_subqueries()

        query = (
            select(Chain, amount_subq.label("c_amount"), count_subq.label("c_count"))
            .options(
                joinedload(Chain.account),
                joinedload(Chain.category),
                selectinload(Chain.operations).joinedload(Operation.category)
            )
            .where(Chain.id == chain_id, Chain.user_id == user_id)
        )

        result = await self.session.execute(query)
        row = result.unique().one_or_none()

        if row:
            chain_obj, amount, count = row
            chain_obj.amount = amount or 0
            chain_obj.operations_count = count or 0
            return chain_obj
        
        return None
    
    async def update(
            self,
            chain: Chain,
            update_data: ChainUpdate
    ) -> Chain:
        data = update_data.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        for key, value in data.items():
            setattr(chain, key, value)

        await self.session.commit()
        await self.session.refresh(chain)

        return chain
    
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
