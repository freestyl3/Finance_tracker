import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from src.chains.models import Chain
from src.base.repository import BaseRepository

class ChainRepository(BaseRepository[Chain]):
    def __init__(self, session: AsyncSession):
        super().__init__(Chain, session)

    async def create(
            self,
            create_data: dict,
            user_id: uuid.UUID
    ) -> Chain:
        chain = Chain(**create_data, user_id=user_id)

        self.session.add(chain)
        await self.session.flush()

        return chain
    
    async def delete(
            self,
            chain_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Chain:
        query = delete(Chain).where(
            Chain.id == chain_id,
            Chain.user_id == user_id
        ).returning(Chain)

        result = await self.session.execute(query)
        return result.scalars().unique().one_or_none()
