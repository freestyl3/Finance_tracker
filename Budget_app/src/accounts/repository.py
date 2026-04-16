import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from src.core.base_repository import BaseRepository
from src.core.enums import RepoAction
from src.accounts.models import Account
from src.common.enums import Currency
from src.accounts.exceptions import AccountAlreadyExistsError, AccountNotFoundError

class AccountRepository(BaseRepository[Account]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Account, session=session)

    def _map_integrity_error(self, repo_action: RepoAction) -> Exception:
        if repo_action == RepoAction.CREATE:
            return AccountAlreadyExistsError()
        return super()._map_integrity_error(repo_action)
    
    def _not_found(self) -> Exception:
        return AccountNotFoundError()
    
    # Удалить эти 2 метода после того как доберусь до OperationService
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
