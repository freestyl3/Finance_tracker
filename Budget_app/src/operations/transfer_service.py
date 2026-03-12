import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from src.operations.transfer_repository import TransferRepository
from src.accounts.repository import AccountRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.operations.schemas import TransferCreate
from src.common.enums import OperationType
from src.operations.models import Operation

class TransferService:
    def __init__(
            self,
            repo: TransferRepository,
            user_category_repository: UserCategoryRepository,
            account_repository: AccountRepository,
    ):
        self.repo = repo
        self.cat_repo = user_category_repository
        self.account_repo = account_repository
        
    async def _validate_account(
            self,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> None:
        try:
            return await self.account_repo.get_by_id(
                model_id=account_id,
                user_id=user_id,
                only_active=True
            )
        except IntegrityError:
            raise ValueError("Could not validate account")
        
    async def _update_account_balance(
            self,
            account_id: uuid.UUID,
            delta: Decimal,
            user_id: uuid.UUID
    ):
        await self.account_repo.update_balance(account_id, delta, user_id)

    async def create(
            self,
            create_data: TransferCreate,
            user_id: uuid.UUID
    ) -> list[Operation]:
        transfer_category = await self.cat_repo.get_one_by(
            user_id=user_id, type=OperationType.TRANSFER
        )
        account_from_id = create_data.account_from
        account_to_id = create_data.account_to

        if account_from_id == account_to_id:
            raise ValueError("You can't create transfer in one account")
        
        await self._validate_account(account_from_id, user_id)
        await self._validate_account(account_to_id, user_id)

        try:
            op_from, op_to = await self.repo.create(
                transfer_data=create_data,
                transfer_category_id=transfer_category.id,
                user_id=user_id
            )

            await self._update_account_balance(
                account_id=create_data.account_from,
                delta=-create_data.amount,
                user_id=user_id
            )

            await self._update_account_balance(
                account_id=create_data.account_to,
                delta=create_data.amount,
                user_id=user_id
            )

            return [op_from, op_to]
        except IntegrityError as e:
            raise ValueError(str(e))
        
    
    