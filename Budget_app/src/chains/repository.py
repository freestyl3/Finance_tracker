import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.chains.schemas import ChainCreate
from src.chains.models import Chain

class ChainRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
            self,
            chain_data: ChainCreate,
            amount: Decimal,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Chain:
        chain = Chain(
            **chain_data.model_dump(exclude=["operation_uuids",]),
            amount=amount,
            account_id=account_id,
            user_id=user_id
        )

        self.session.add(chain)
        await self.session.flush()

        return chain