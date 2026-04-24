import uuid
from decimal import Decimal

from sqlalchemy.orm import joinedload

from src.core.uow import IUnitOfWork
from src.operations.repository import OperationRepository
from src.operations.schemas import OperationCreate, OperationUpdate
from src.operations.models import Operation
from src.pagination import PaginationParams
from src.operations.filters import OperationFilter
from src.accounts.repository import AccountRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.common.enums import OperationType, Currency
from src.accounts.models import Account
from src.categories.user_categories.models import UserCategory
from src.operations.exceptions import (
    OperationNotFoundError, OperationInChainError, OperationIsTransferError
)
from src.accounts.exceptions import AccountNotFoundError
from src.categories.user_categories.exceptions import UserCategoryNotFoundError

class OperationService:
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
        category = await self.cat_repo.get_one_by(
            user_id=user_id,
            id=category_id,
            is_active=True
        )

        if not category:
            raise UserCategoryNotFoundError()
        
        return category
        
    async def _update_account_balance(
            self,
            account_id: uuid.UUID,
            delta: Decimal,
            user_id: uuid.UUID,
            currency: Currency | None = None,
    ) -> Account:
        account = await self.acc_repo.update_balance(
            account_id=account_id,
            delta=delta,
            user_id=user_id,
            currency=currency
        )

        if not account:
            raise AccountNotFoundError()
        
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

        data_dict["amount"] = self._validate_amount(category.type, create_data.amount)
        
        operation = await self.op_repo.create(
            create_data=data_dict,
            user_id=user_id
        )

        account = await self._update_account_balance(
            account_id=operation.account_id,
            delta=operation.amount,
            user_id=user_id
        )

        operation.account = account
        operation.category = category

        return operation

    async def get_all(
            self,
            user_id: uuid.UUID,
            pagination: PaginationParams,
            filters: OperationFilter | None = None
    ) -> list[Operation]:
        return await self.op_repo.get_all(user_id, filters, pagination)
    
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

        operation = await self.op_repo.update(
            model_id=operation_id,
            update_data=data_dict,
            user_id=user_id,
        )

        if operation.chain_id:
            raise OperationInChainError()
        
        if operation.related_operation_id:
            raise OperationIsTransferError()

        return await self.op_repo.get_one_by(
            user_id,
            True,
            joinedload(Operation.account),
            joinedload(Operation.category),
            id=operation_id
        )
    
    async def update_with_related_data(
            self,
            operation_id: uuid.UUID,
            update_data: OperationUpdate,
            user_id: uuid.UUID
    ) -> Operation:
        operation = await self.op_repo.get_one_by(
            user_id,
            True,
            joinedload(Operation.account),
            joinedload(Operation.category),
            id=operation_id
        )

        if not operation:
            raise OperationNotFoundError()
        
        if operation.chain_id:
            raise OperationInChainError()
        
        if operation.related_operation_id:
            raise OperationIsTransferError()
        
        amount = update_data.amount or operation.amount
        account = operation.account
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
        data_dict["amount"] = new_amount

        updated_operation = await self.op_repo.update(
            model_id=operation_id,
            update_data=data_dict,
            user_id=user_id
        )
    
        updated_operation.account = account
        updated_operation.category = category
    
        return updated_operation       

    async def delete(self, operation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        deleted_op = await self.op_repo.delete(
            model_id=operation_id,
            user_id=user_id
        )

        if not deleted_op:
            return True
        
        if deleted_op.chain_id:
            raise OperationInChainError()
        
        if deleted_op.related_operation_id:
            raise OperationIsTransferError(
                message="Can't edit transfer on this endpoint. Use DELETE /transfers/{transfer_id}"
            )

        await self._update_account_balance(
            account_id=deleted_op.account_id,
            delta=-deleted_op.amount,
            user_id=user_id
        )

        return True
            
    # async def get_operations_stats(self, user_id: int, filters: ReportFilter):
    #     check_date_order(filters)
    #     return await self.repo.get_operations_stats(user_id, filters)
    
    # async def get_operations_report(self, user_id: int, filters: ReportFilter):
    #     check_date_order(filters)
    #     report_data = await self.repo.get_operations_stats(
    #         user_id=user_id,
    #         filter_params=filters
    #     )

    #     csv_file = generate_csv_report(report_data)

    #     filename = f"report_{filters.date_from}_{filters.date_to}.csv"

    #     return csv_file, filename

    # async def get_monthly_operations(
    #     self,
    #     year: int | None,
    #     month: int | None,
    #     user_id: int
    # ):
    #     today = date.today()
    #     target_year = year if year else today.year
    #     target_month = month if month else today.month

    #     first_day, last_day = get_month_range(target_year, target_month)

    #     filters = ReportFilter(
    #         date_from=first_day,
    #         date_to=last_day
    #     )

    #     return await self.get_operations_stats(user_id, filters)