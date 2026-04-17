import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from src.core.uow import IUnitOfWork
from src.transfers.repository import TransferRepository
from src.accounts.repository import AccountRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.transfers.schemas import TransferCreate, TransferUpdate
from src.common.enums import OperationType
from src.operations.models import Operation
from src.accounts.models import Account
from src.operations.repository import OperationRepository

class TransferService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    @property
    def trans_repo(self) -> TransferRepository:
        return self.uow.get_repo(TransferRepository)
    
    @property
    def op_repo(self) -> OperationRepository:
        return self.uow.get_repo(OperationRepository)
    
    @property
    def cat_repo(self) -> UserCategoryRepository:
        return self.uow.get_repo(OperationRepository)
    
    @property
    def acc_repo(self) -> AccountRepository:
        return self.uow.get_repo(UserCategoryRepository)
        
    async def _validate_account(
            self,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Account:
        acc = await self.acc_repo.get_one_by(
                user_id=user_id,
                id=account_id,
                is_active=True
            )
        
        if not acc:
            raise ValueError("Can't validate account")
        return acc
    
    async def _validate_accounts_for_transfer(
            self,
            account_from_id: uuid.UUID,
            account_to_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> None:
        if account_from_id == account_to_id:
            raise ValueError("Can't create transfer in the same account")
        
        from_acc = await self._validate_account(account_from_id, user_id)
        new_acc = await self._validate_account(account_to_id, user_id)

        if from_acc.currency != new_acc.currency:
            raise ValueError("Can't create transfer in accounts with different currency")
        
    async def _update_account_balance(
            self,
            account_id: uuid.UUID,
            delta: Decimal,
            user_id: uuid.UUID
    ):
        await self.acc_repo.update_balance(account_id, delta, user_id)

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

        await self._validate_accounts_for_transfer(
            account_from_id=account_from_id,
            account_to_id=account_to_id,
            user_id=user_id
        )

        try:
            op_from, op_to = await self.trans_repo.create(
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
        
    async def update(
            self,
            operation_id: uuid.UUID,
            update_data: TransferUpdate,
            user_id: uuid.UUID
    ) -> list[Operation]:
        operation = await self.op_repo.get_one_by(
            user_id=user_id,
            operation_id=operation_id
        )
        related_operation_id = operation.related_operation_id

        if not related_operation_id:
            raise ValueError("Can't update operation in this endpoint. Use PUT /operations/{operation_id}")
        
        related_operation = await self.trans_repo.get_related_operation(
            related_operation_id=related_operation_id,
            user_id=user_id
        )

        if operation.amount < 0:
            operation_from, operation_to = operation, related_operation
        else:
            operation_from, operation_to = related_operation, operation

        account_from_id = update_data.account_from_id or operation_from.account_id
        account_to_id = update_data.account_to_id or operation_to.account_id

        await self._validate_accounts_for_transfer(
            account_from_id=account_from_id,
            account_to_id=account_to_id,
            user_id=user_id
        )
        
        op_from, op_to = await self.trans_repo.update(
            operation_from=operation_from,
            operation_to=operation_to,
            update_data=update_data
        )

        return [op_from, op_to]
    