from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.expenses.models import Expense, ExpenseCategory
from src.expenses.schemas import ExpenseCreate, ExpenseUpdate

class ExpenseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_expense(self, expense_data: ExpenseCreate, user_id: int) -> Expense:
        expense = Expense(**expense_data.model_dump(), user_id=user_id)
        self.session.add(expense)
        await self.session.commit()
        await self.session.refresh(expense)
        return expense
    
    async def check_category_owner(self, category_id: int, user_id: int) -> bool:
        query = select(ExpenseCategory.id).where(
            ExpenseCategory.id == category_id,
            ExpenseCategory.user_id == user_id
        )

        result = await self.session.execute(query)
        return result.scalars().one_or_none() is not None
    
    async def get_expenses(self, user_id: int) -> list[Expense]:
        query = select(Expense).where(Expense.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_expense_by_id(self, expense_id: int, user_id: int) -> Expense | None:
        query = select(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()
    
    async def delete_expense(self, expense_id: int, user_id: int) -> bool:
        query = delete(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == user_id
        )
        result = await self.session.execute(query)
        await self.session.commit()

        return result.rowcount > 0
    
    async def update_expense(
            self,
            expense_id: int,
            user_id: int,
            expense_update: ExpenseUpdate
    ) -> Expense | None:
        expense = await self.get_expense_by_id(expense_id, user_id)
        if not expense:
            return None
        
        update_data = expense_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(expense, key, value)

        await self.session.commit()
        await self.session.refresh(expense)

        return expense
