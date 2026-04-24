import uuid
import uuid6
from decimal import Decimal
from collections import defaultdict

from sqlalchemy.orm import joinedload

from src.core.uow import IUnitOfWork
from src.accounts.repository import AccountRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.transfers.schemas import TransferCreate, TransferUpdate
from src.common.enums import OperationType
from src.operations.models import Operation
from src.accounts.models import Account
from src.operations.repository import OperationRepository
from src.transfers.exceptions import (
    SameAccountTransferError, DifferentCurrencyInTransferError,
    TransferIsOperationError, TransferNotFoundError
)
from src.accounts.exceptions import AccountNotFoundError

class TransferService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow
    
    @property
    def op_repo(self) -> OperationRepository:
        return self.uow.get_repo(OperationRepository)
    
    @property
    def cat_repo(self) -> UserCategoryRepository:
        return self.uow.get_repo(UserCategoryRepository)
    
    @property
    def acc_repo(self) -> AccountRepository:
        return self.uow.get_repo(AccountRepository)
        
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
            raise AccountNotFoundError()
        return acc
    
    async def _validate_accounts_for_transfer(
            self,
            account_from_id: uuid.UUID,
            account_to_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> tuple[uuid.UUID]:
        if account_from_id == account_to_id:
            raise SameAccountTransferError()
        
        from_acc = await self._validate_account(account_from_id, user_id)
        new_acc = await self._validate_account(account_to_id, user_id)

        if from_acc.currency != new_acc.currency:
            raise DifferentCurrencyInTransferError()
        
        return from_acc, new_acc

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

        account_from, account_to = await self._validate_accounts_for_transfer(
            account_from_id=account_from_id,
            account_to_id=account_to_id,
            user_id=user_id
        )

        from_id = uuid6.uuid7()
        to_id = uuid6.uuid7()

        operations = [
            {
                "id": from_id,
                "amount": -create_data.amount,
                "description": create_data.description,
                "account_id": create_data.account_from,
                "category_id": transfer_category.id,
                "related_operation_id": to_id
            },
            {
                "id": to_id,
                "amount": create_data.amount,
                "description": create_data.description,
                "account_id": create_data.account_to,
                "category_id": transfer_category.id,
                "related_operation_id": from_id
            }
        ]

        created_operations = list(
            await self.op_repo.batch_create(
                create_data_list=operations,
                user_id=user_id
            )
        )

        await self.acc_repo.update_balance(
            account_id=create_data.account_from,
            delta=-create_data.amount,
            user_id=user_id
        )

        await self.acc_repo.update_balance(
            account_id=create_data.account_to,
            delta=create_data.amount,
            user_id=user_id
        )

        created_operations[0].account = account_from
        created_operations[0].category = transfer_category

        created_operations[1].account = account_to
        created_operations[1].category = transfer_category

        return created_operations    
        
    async def update(
            self,
            operation_id: uuid.UUID,
            update_data: TransferUpdate,
            user_id: uuid.UUID
    ) -> list[Operation]:
        operation = await self.op_repo.get_one_by(
            user_id,
            True,
            joinedload(Operation.category),
            joinedload(Operation.account),
            id=operation_id
        )

        if not operation:
            raise TransferNotFoundError()
        
        if not operation.related_operation_id:
            raise TransferIsOperationError()
        
        related_operation = await self.op_repo.get_one_by(
            user_id,
            True,
            joinedload(Operation.category),
            joinedload(Operation.account),
            id=operation.related_operation_id,
        )

        account_from = operation.account
        account_to = related_operation.account

        if operation.amount < 0:
            op_from, op_to = operation, related_operation
        else:
            op_from, op_to = related_operation, operation

        base_data = update_data.model_dump(
            exclude={"amount", "account_from_id", "account_to_id"},
            exclude_unset=True
        )
        
        data_from = {**base_data}
        data_to = {**base_data}

        has_financial_changes = any(
            [
                update_data.amount is not None,
                update_data.account_from_id is not None,
                update_data.account_to_id is not None
            ]
        )

        if has_financial_changes:
            new_amount = update_data.amount or op_to.amount
            new_acc_from = update_data.account_from_id or op_from.account_id
            new_acc_to = update_data.account_to_id or op_to.account_id

            account_from, account_to = await self._validate_accounts_for_transfer(
                account_from_id=new_acc_from,
                account_to_id=new_acc_to,
                user_id=user_id
            )

            deltas = defaultdict(Decimal)

            deltas[op_from.account_id] -= op_from.amount
            deltas[op_to.account_id] -= op_to.amount

            deltas[new_acc_from] -= new_amount
            deltas[new_acc_to] += new_amount

            for acc_id, delta in deltas.items():
                if delta != 0:
                    await self.acc_repo.update_balance(
                        account_id=acc_id, 
                        delta=delta, 
                        user_id=user_id
                    )

            data_from["amount"] = -new_amount
            data_from["account_id"] = new_acc_from

            data_to["amount"] = new_amount
            data_to["account_id"] = new_acc_to

        updated_op_from = await self.op_repo.update(
            model_id=op_from.id,
            update_data=data_from,
            user_id=user_id
        )
        
        updated_op_to = await self.op_repo.update(
            model_id=op_to.id,
            update_data=data_to,
            user_id=user_id
        )

        updated_op_from.account = account_from
        updated_op_to.account = account_to

        return[updated_op_from, updated_op_to]
    
    async def delete(
            self,
            operation_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool:
        operation = await self.op_repo.delete(
            model_id=operation_id,
            user_id=user_id
        )

        if not operation:
            return True

        if not operation.related_operation_id:
            raise TransferIsOperationError(
                message="Can't edit operation on this endpoint. Use DELETE /operations/{operation_id}"
            )
        
        related_operation = await self.op_repo.delete(
            model_id=operation.related_operation_id,
            user_id=user_id
        )

        await self.acc_repo.update_balance(
            account_id=operation.account_id,
            delta=-operation.amount,
            user_id=user_id
        )

        await self.acc_repo.update_balance(
            account_id=related_operation.account_id,
            delta=-related_operation.amount,
            user_id=user_id
        )

        return True
    