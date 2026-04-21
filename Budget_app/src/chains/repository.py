import uuid
from typing import override

from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.chains.models import Chain
from src.operations.models import Operation
from src.core.repository.scoped import UserScopedRepository
from src.chains.exceptions import ChainNotFoundError

class ChainRepository(UserScopedRepository[Chain]):
    def __init__(self, session: AsyncSession):
        super().__init__(Chain, session)

    @override
    def _not_found(self) -> Exception:
        return ChainNotFoundError()

    @override
    async def get_one_by(
        self,
        user_id: uuid.UUID,
        unique: bool = True,
        *load_options,
        **fields
    ) -> Chain:
        load_options += (
            joinedload(Chain.category),
            selectinload(Chain.operations).joinedload(Operation.category),
            selectinload(Chain.operations).joinedload(Operation.account),
        )

        return await super().get_one_by(user_id, unique, *load_options, **fields)
    
    @override
    async def get_all_by(
        self,
        user_id: uuid.UUID,
        unique: bool = True,
        *load_options,
        **fields
    ) -> Sequence[Chain]:
        load_options += (
            joinedload(Chain.category),
        )
        return await super().get_all_by(user_id, unique, *load_options, **fields)
    