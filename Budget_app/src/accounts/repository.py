import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.base.repository import BaseRepository
from src.accounts.models import Account
from src.accounts.schemas import AccountCreate, AccountUpdate

class AccountRepository(BaseRepository[Account, AccountUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Account, session=session)

    async def create(
            self,
            account_data: AccountCreate,
            user_id: uuid.UUID
    ) -> Account:
        data_dict = account_data.model_dump()
        existing_account = await self.get_by_name(
            account_data.name,
            user_id
        )

        if not existing_account:
            account = Account(**data_dict, user_id=user_id)
            self.session.add(account)
        else:
            account = existing_account
            account.is_active = True

            for key, value in data_dict.items():
                setattr(account, key, value)

        await self.session.commit()
        await self.session.refresh(account)
        return account
