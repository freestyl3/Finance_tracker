from sqlalchemy import select, delete, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.operations.expenses.models import Expense, ExpenseCategory
from src.operations.expenses.schemas import ExpenseCreate, ExpenseUpdate, ExpenseFilter
from src.reports.schemas import ReportFilter
from Budget_app.src.base.operaion_repository import BaseOperationRepository
from src.pagination import PaginationParams


class ExpenseRepository(BaseOperationRepository):
    async def create_expense(
            self,
            expense_data: ExpenseCreate,
            user_id: int
    ) -> Expense:
        return await super().create(expense_data, user_id)
    
    async def get_expenses(
            self,
            user_id: int,
            filter_params: ExpenseFilter,
            pagination: PaginationParams
    ) -> list[Expense]:
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
    ) -> Expense | None:
        return await super().get_operation_by_id(expense_id, user_id)
    
    async def delete_expense(self, expense_id: int, user_id: int) -> bool:
        return await super().delete_operation(expense_id, user_id)
    
    async def update_expense(
            self,
            expense_id: int,
            user_id: int,
            expense_update: ExpenseUpdate
    ) -> Expense | None:
        return await super().update_operation(expense_id, user_id, expense_update)
    
# class ExpenseRepository:
#     def __init__(self, session: AsyncSession):
#         self.session = session

#     def _apply_report_filters(self, query, filters: ExpenseFilter):
#         if filters.category_id:
#             query = query.where(Expense.category_id == filters.category_id)
#         if filters.date_from:
#             query = query.where(Expense.date >= filters.date_from)
#         if filters.date_to:
#             query = query.where(Expense.date <= filters.date_to)
#         return query

#     async def create_expense(self, expense_data: ExpenseCreate, user_id: int) -> Expense:
#         expense = Expense(**expense_data.model_dump(), user_id=user_id)
#         self.session.add(expense)
#         await self.session.commit()
#         await self.session.refresh(expense)
#         return expense
    
#     async def check_category_owner(self, category_id: int, user_id: int) -> bool:
#         query = select(ExpenseCategory.id).where(
#             ExpenseCategory.id == category_id,
#             ExpenseCategory.user_id == user_id
#         )

#         result = await self.session.execute(query)
#         return result.scalars().one_or_none() is not None
    
#     async def get_expenses(
#             self,
#             user_id: int,
#             filter_params: ExpenseFilter
#     ) -> list[Expense]:
#         query = (
#             select(Expense)
#             .options(joinedload(Expense.category))
#             .where(Expense.user_id == user_id)
#         )
#         query = self._apply_report_filters(query, filter_params)
#         query = query.order_by(Expense.date.desc())
#         query = query.limit(filter_params.limit).offset(filter_params.offset)

#         result = await self.session.execute(query)
#         return list(result.scalars().all())
    
#     async def get_total_amount(
#             self,
#             user_id: int,
#             filters: ReportFilter
#     ) -> float:
#         query = select(
#             func.sum(Expense.amount).label("total")
#         ).where(Expense.user_id == user_id)

#         query = self._apply_report_filters(query, filters)

#         result = await self.session.execute(query)

#         return result.scalar() or 0.0
    
#     async def get_expenses_stats(
#             self,
#             user_id: int,
#             filter_params: ReportFilter
#     ) -> dict:
#         total_amount = func.sum(Expense.amount).label("total_amount")

#         query = (
#             select(
#                 Expense.category_id,
#                 ExpenseCategory.name.label("category_name"),
#                 total_amount
#             )
#             .join(ExpenseCategory, Expense.category_id == ExpenseCategory.id)
#             .where(Expense.user_id == user_id)
#             .group_by(Expense.category_id, ExpenseCategory.name)
#             .order_by(total_amount.desc())
#         )

#         query = self._apply_report_filters(query, filter_params)

#         grouped_result = await self.session.execute(query)
#         total_sum = await self.get_total_amount(user_id, filter_params)

#         return {
#             "total_sum": total_sum,
#             "categories": grouped_result.mappings().all()
#         }
    
#     async def get_expense_by_id(self, expense_id: int, user_id: int) -> Expense | None:
#         query = select(Expense).where(
#             Expense.id == expense_id,
#             Expense.user_id == user_id
#         )
#         result = await self.session.execute(query)
#         return result.scalars().one_or_none()
    
#     async def delete_expense(self, expense_id: int, user_id: int) -> bool:
#         query = delete(Expense).where(
#             Expense.id == expense_id,
#             Expense.user_id == user_id
#         )
#         result = await self.session.execute(query)
#         await self.session.commit()

#         return result.rowcount > 0
    
#     async def update_expense(
#             self,
#             expense_id: int,
#             user_id: int,
#             expense_update: ExpenseUpdate
#     ) -> Expense | None:
#         expense = await self.get_expense_by_id(expense_id, user_id)
#         if not expense:
#             return None
        
#         update_data = expense_update.model_dump(exclude_unset=True)

#         for key, value in update_data.items():
#             setattr(expense, key, value)

#         await self.session.commit()
#         await self.session.refresh(expense)

#         return expense
