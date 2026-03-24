import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import set_committed_value

from src.operations.repository import OperationRepository
from src.operations.schemas import OperationCreate, OperationUpdate
from src.operations.models import Operation
from src.pagination import PaginationParams
from src.operations.filters import OperationFilter
from src.accounts.repository import AccountRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.common.enums import OperationType
from src.accounts.models import Account
from src.categories.user_categories.models import UserCategory


class OperationService:
    def __init__(
            self,
            repo: OperationRepository,
            user_category_repository: UserCategoryRepository,
            account_repository: AccountRepository
    ):
        self.repo = repo
        self.cat_repo = user_category_repository
        self.account_repo = account_repository
    
    def _validate_amount(
            self,
            category: UserCategory,
            amount: Decimal
    ) -> Decimal:        
        if category.type == OperationType.EXPENSE:
            return -amount
        return amount
        
    async def _validate_account(
            self,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Account:
        acc = await self.account_repo.get_by_id(
            model_id=account_id,
            user_id=user_id,
            only_active=True
        )
    
        if not acc:
            raise ValueError("Can't validate account")
        return acc
    
    async def _validate_category(
            self,
            category_id: uuid.UUID,
            user_id: uuid.UUID,
            only_active: bool = True
    ) -> UserCategory:
        category = await self.cat_repo.get_by_id(
            model_id=category_id,
            user_id=user_id,
            only_active=only_active
        )

        if not category:
            raise ValueError("Can't validate category")
        return category
        
    async def _update_account_balance(
            self,
            account_id: uuid.UUID,
            delta: Decimal,
            user_id: uuid.UUID,
            is_active: bool = True
    ):
        account = await self.account_repo.update_balance(
            account_id=account_id,
            delta=delta,
            user_id=user_id,
            is_active=is_active
        )

        if not account:
            await self.repo.session.rollback()
            raise ValueError("Account not found")
        return account

    async def create(
            self,
            create_data: OperationCreate,
            user_id: uuid.UUID,
            system_operation: bool = False
    ) -> Operation:
        category = await self._validate_category(
            category_id=create_data.category_id,
            user_id=user_id,
            only_active=not(system_operation)
        )

        create_data.amount = self._validate_amount(category, create_data.amount)
        
        try:
            operation = await self.repo.create(
                operation_data=create_data,
                user_id=user_id
            )

            account = await self._update_account_balance(
                create_data.account_id,
                create_data.amount,
                user_id
            )

            await self.repo.session.commit()

            await self.repo.session.refresh(operation)

            set_committed_value(operation, "account", account)
            set_committed_value(operation, "category", category)

        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))

        return operation

    async def get_all(
            self,
            user_id: uuid.UUID,
            pagination: PaginationParams,
            filters: OperationFilter | None = None
    ) -> list[Operation]:
        return await self.repo.get_all(user_id, filters, pagination)
    
    async def update(
            self,
            operation_id: uuid.UUID,
            update_data: OperationUpdate,
            user_id: uuid.UUID
    ):
        operation = await self.repo.get_by_id(operation_id, user_id)

        if not operation:
            raise ValueError("Operation not found or you don't have permission")
        
        if operation.chain_id:
            raise ValueError("Can't delete operation inside chain. Remove operation from chain first")

        account_id = update_data.account_id or operation.account_id
        category_id = update_data.category_id or operation.category_id
        amount = update_data.amount or operation.amount

        if operation.related_operation_id:
            raise ValueError("Can't update transfer on this endpoint. Use PUT /transfers/{operation_id}")

        if update_data.account_id and update_data.account_id != operation.account_id:
            new_account = await self._validate_account(
                account_id=update_data.account_id,
                user_id=user_id
            )

            if operation.account.currency != new_account.currency:
                raise ValueError("Can't update accounts with different currency")

        new_amount = await self._validate_amount(
            amount=abs(amount),
            category_id=category_id,
            user_id=user_id
        )

        if new_amount != operation.amount or account_id != operation.account_id:
            if account_id == operation.account_id:
                delta = -operation.amount + new_amount

                account = await self._update_account_balance(
                    account_id=account_id,
                    delta=delta,
                    user_id=user_id
                )
            else:
                await self._update_account_balance(
                    account_id=operation.account_id,
                    delta=-operation.amount,
                    user_id=user_id,
                    is_active=False
                )

                account = await self._update_account_balance(
                    account_id=account_id,
                    delta=new_amount,
                    user_id=user_id
                )
        
        update_data.amount = new_amount

        try:
            updated_operation = await self.repo.update(operation, update_data)

            await self.repo.session.refresh(account)
        except IntegrityError as e:
            raise ValueError(str(e))

        if not updated_operation:
            raise ValueError("Operation not found or you don't have permission")
        
        return updated_operation

    async def delete(self, operation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        operation = await self.repo.get_by_id(operation_id, user_id)
        
        if not operation:
            raise ValueError("Operation not found or you don't have permission")
        
        if operation.chain_id:
            raise ValueError("Can't delete operation inside chain. Remove operation from chain first")
        
        await self._update_account_balance(
            account_id=operation.account_id,
            delta=-operation.amount,
            user_id=user_id
        )

        if operation.related_operation_id:
            related_operation = await self.repo.get_by_id(
                operation.related_operation_id,
                user_id
            )

            await self._update_account_balance(
                account_id=related_operation.account_id,
                delta=-related_operation.amount,
                user_id=user_id
            )

            await self.repo.delete(related_operation)

        return await self.repo.delete(operation)
    
    async def change_visibility(
            self,
            operation_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Operation:        
        operation = await self.repo.change_visibility(operation_id, user_id)

        if not operation:
            raise ValueError("Operation not found")
        return operation
            