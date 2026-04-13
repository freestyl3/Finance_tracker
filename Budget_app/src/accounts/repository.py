import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, delete
from sqlalchemy.exc import IntegrityError

from src.base.repository import ActiveNamedRepository
from src.accounts.models import Account
from src.common.enums import Currency
from src.accounts.exceptions import AccountAlreadyExistsError, AccountNotFoundError

class AccountRepository(ActiveNamedRepository[Account]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Account, session=session)

    async def create(
            self,
            create_data: dict,
            user_id: uuid.UUID
    ) -> Account:
        account = await super().create(create_data, user_id)
        
        try:
            await self.session.flush()
            return account
        except IntegrityError:
            raise AccountAlreadyExistsError()

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

    async def delete(
            self,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool:
        query = delete(Account).where(
            Account.id == account_id,
            Account.user_id == user_id,
            Account.is_active.is_(True)
        )

        result = await self.session.execute(query)

        if not result.rowcount > 0:
            raise AccountNotFoundError()
        return True
        
    async def soft_delete(
            self,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool:
        query = update(Account).where(
            Account.id == account_id,
            Account.user_id == user_id,
            Account.is_active.is_(True)
        ).values(is_active=False)

        result = await self.session.execute(query)

        if not result.rowcount > 0:
            raise AccountNotFoundError()
        return True