import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, update

from src.base.repository import ActiveNamedRepository
from src.accounts.models import Account
from src.accounts.schemas import AccountCreate, AccountUpdate

class AccountRepository(ActiveNamedRepository[Account, AccountUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Account, session=session)

    async def create(
            self,
            account_data: AccountCreate,
            user_id: uuid.UUID
    ) -> Account:
        account = Account(**account_data.model_dump(), user_id=user_id)

        self.session.add(account)
        return account

    async def restore(
            self,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Account:
        query = (
            update(Account)
            .where(
                Account.id == account_id,
                Account.user_id == user_id
            )
            .values(is_active=True)
            .returning(Account)
        )

        result = await self.session.scalars(query)
        return result.unique().one_or_none()
    
    async def update_balance(
            self,
            account_id: uuid.UUID,
            delta: Decimal,
            user_id: uuid.UUID,
            is_active: bool = True
    ) -> Account | None:
        query = (
            update(Account)
            .where(
                Account.id == account_id,
                Account.user_id == user_id
            )
            .values(
                balance=(Account.balance + delta)
            )
            .returning(Account)
        )

        if is_active:
            query = query.where(Account.is_active.is_(True))

        result = await self.session.scalars(query)
        return result.unique().one_or_none()
