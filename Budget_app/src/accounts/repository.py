import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.accounts.models import Account
from src.accounts.schemas import AccountCreate, AccountUpdate

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
    
    async def get_account_by_id(
            self,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Account | None:
        query = select(Account).where(
            Account.id == account_id,
            Account.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    
    async def update_account(
            self,
            account_data: AccountUpdate,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Account | None:
        account = await self.get_account_by_id(account_id, user_id)

        if not account:
            return None
        
        update_data = account_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(account, key, value)

        await self.session.commit()
        await self.session.refresh(account)

        return account