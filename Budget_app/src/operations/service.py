import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from src.operations.repositories.repository import OperationRepository
from src.operations.schemas import OperationCreate, OperationUpdate
from src.operations.models import Operation
from src.pagination import PaginationParams
from src.operations.filters import OperationFilter
from src.accounts.repository import AccountRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.common.enums import OperationType, Currency
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
            category_type: OperationType,
            amount: Decimal
    ) -> Decimal:        
        if category_type == OperationType.EXPENSE:
            return -amount
        return amount
    
    async def _validate_category(
            self,
            category_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> UserCategory:
        category = await self.cat_repo.get_by_id(
            model_id=category_id,
            user_id=user_id
        )

        if not category:
            raise ValueError("Can't validate category")
        return category
        
    async def _update_account_balance(
            self,
            account_id: uuid.UUID,
            delta: Decimal,
            user_id: uuid.UUID,
            currency: Currency | None = None,
    ) -> Account:
        account = await self.account_repo.update_balance(
            account_id=account_id,
            delta=delta,
            user_id=user_id,
            currency=currency
        )

        if not account:
            raise ValueError("Account not found")
        return account

    async def create(
            self,
            create_data: OperationCreate,
            user_id: uuid.UUID
    ) -> Operation:
        data_dict = create_data.model_dump(exclude_unset=True)

        category = await self._validate_category(
            category_id=create_data.category_id,
            user_id=user_id
        )

        # create_data.amount = self._validate_amount(category.type, create_data.amount)
        data_dict["amount"] = self._validate_amount(category.type, create_data.amount)
        
        try:
            operation = await self.repo.create(
                create_data=data_dict,
                user_id=user_id
            )

            await self._update_account_balance(
                account_id=operation.account_id,
                delta=operation.amount,
                user_id=user_id
            )

            await self.repo.session.commit()
            await self.repo.session.refresh(operation, ["account", "category"])

            return operation

        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))

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
    ) -> Operation:
        if update_data.amount or update_data.account_id or update_data.category_id:
            return await self.update_with_related_data(
                operation_id=operation_id,
                update_data=update_data,
                user_id=user_id
            )
        return await self.update_without_related_data(
            operation_id=operation_id,
            update_data=update_data,
            user_id=user_id
        )

    async def update_without_related_data(
            self,
            operation_id: uuid.UUID,
            update_data: OperationUpdate,
            user_id: uuid.UUID
    ) -> Operation:
        data_dict = update_data.model_dump(exclude_unset=True)

        try:
            await self.repo.update(
                model_id=operation_id,
                update_data=data_dict,
                user_id=user_id,
            )

            await self.repo.session.commit()
            return await self.repo.get_by_id(
                operation_id,
                user_id,
                joinedload(Operation.account),
                joinedload(Operation.category)
            )
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))
    
    async def update_with_related_data(
            self,
            operation_id: uuid.UUID,
            update_data: OperationUpdate,
            user_id: uuid.UUID
    ):
        operation = await self.repo.get_by_id(
            operation_id,
            user_id,
            joinedload(Operation.category),
            joinedload(Operation.account)
        )

        if not operation:
            raise ValueError("Operation not found or you don't have permission")
        
        if operation.chain_id:
            raise ValueError("Can't delete operation inside chain. Remove operation from chain first")
        
        if operation.related_operation_id:
            raise ValueError("Can't update transfer on this endpoint. Use PUT /transfers/{operation_id}")
        
        try:
            amount = update_data.amount or operation.amount
            category = operation.category

            if update_data.category_id and operation.category_id != update_data.category_id:
                category = await self._validate_category(update_data.category_id, user_id)

            new_amount = self._validate_amount(
                category_type=category.type,
                amount=abs(amount)            
            )

            account_id = update_data.account_id or operation.account_id

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
                        user_id=user_id
                    )

                    account = await self._update_account_balance(
                        account_id=account_id,
                        delta=new_amount,
                        user_id=user_id,
                        currency=operation.account.currency
                    )
            
            data_dict = update_data.model_dump(exclude_unset=True)
            # update_data.amount = new_amount
            data_dict["amount"] = new_amount

            updated_operation = await self.repo.update(
                model_id=operation_id,
                update_data=data_dict,
                user_id=user_id
            )

            if not updated_operation:
                raise ValueError("Operation not found or you don't have permission")
        
            await self.repo.session.commit()
            await self.repo.session.refresh(operation, ["account", "category"])
        
            return updated_operation
            
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))
        except ValueError as e:
            await self.repo.session.rollback()
            raise e        

    async def delete(self, operation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        try:
            deleted_operations: list[Operation] = list(
                await self.repo.delete(operation_id, user_id)
            )
            
            if not deleted_operations:
                raise ValueError("Operation not found or you don't have permission")
            
            if deleted_operations[0].chain_id:
                raise ValueError("Can't delete operation inside chain. Remove operation from chain first")
            
            data_dict = {}

            for operation in deleted_operations:
                data_dict[operation.account_id] = operation.amount

            await self.account_repo.batch_update_balance(
                data_dict=data_dict,
                user_id=user_id
            )

            await self.repo.session.commit()
            return True
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))
        except ValueError as e:
            await self.repo.session.rollback()
            raise e
    
    async def change_visibility(
            self,
            operation_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Operation:        
        operation = await self.repo.change_visibility(operation_id, user_id)

        if not operation:
            raise ValueError("Operation not found")
        return operation
            