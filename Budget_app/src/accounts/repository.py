import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.accounts.models import Account
from src.accounts.schemas import AccountCreate

class AccountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
            self,
            account_data: AccountCreate,
            user_id: uuid.UUID
    ) -> Account:
        account = Account(**account_data.model_dump(), user_id=user_id)

        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def get_accounts(self, user_id: uuid.UUID) -> list[Account]:
        query = select(Account).where(Account.user_id == user_id)

        result = await self.session.execute(query)
        return list(result.scalars().all())