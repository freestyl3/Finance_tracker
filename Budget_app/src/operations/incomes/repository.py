from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from Budget_app.src.base.operaion_repository import BaseOperationRepository
from src.pagination import PaginationParams
from src.operations.incomes.models import Income, IncomeCategory
from src.operations.incomes.schemas import IncomeCreate, IncomeUpdate, IncomeFilter
from src.reports.schemas import ReportFilter

class IncomeRepository(BaseOperationRepository):
    async def create_expense(
            self,
            expense_data: IncomeCreate,
            user_id: int
    ) -> Income:
        return await super().create(expense_data, user_id)
    
    async def get_expenses(
            self,
            user_id: int,
            filter_params: IncomeFilter,
            pagination: PaginationParams
    ) -> list[Income]:
        return await super().get_operations(user_id, filter_params, pagination)
    
    async def get_expenses_stats(
            self,
            user_id: int, 
            filter_params: ReportFilter
    ) -> dict:
        return await super().get_operations_stats(user_id, filter_params)

    async def get_expense_by_id(
            self,
            expense_id: int,
            user_id: int
    ) -> Income | None:
        return await super().get_operation_by_id(expense_id, user_id)
    
    async def delete_expense(self, expense_id: int, user_id: int) -> bool:
        return await super().delete_operation(expense_id, user_id)
    
    async def update_expense(
            self,
            expense_id: int,
            user_id: int,
            expense_update: IncomeUpdate
    ) -> Income | None:
        return await super().update_operation(expense_id, user_id, expense_update)
