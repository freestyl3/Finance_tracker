import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, update

from src.base.repository import ActiveNamedRepository
from src.accounts.models import Account
from src.accounts.schemas import AccountCreate, AccountUpdate
from src.common.enums import Currency

class AccountRepository(
    ActiveNamedRepository[Account, AccountCreate, AccountUpdate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Account, session=session)

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
            currency: Currency | None = None
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

        if currency:
            query = query.where(Account.currency == currency)

        result = await self.session.scalars(query)
        return result.unique().one_or_none()

    async def batch_update_balance(
            self,
            data_dict: dict,
            user_id
    ) -> None:
        for account_id, amount in data_dict.items():
            query = update(Account).where(
                Account.id == account_id,
                Account.user_id == user_id
            ).values(
                balance=(Account.balance - amount)
            )

            await self.session.execute(query)
    