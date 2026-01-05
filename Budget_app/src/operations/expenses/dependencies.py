from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.operations.expenses.models import Expense, ExpenseCategory
from src.operations.expenses.repository import ExpenseRepository
from src.database.db_helper import db_helper
from src.operations.expenses.service import ExpenseService

async def get_expenses_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> ExpenseRepository:
    return ExpenseRepository(session, Expense, ExpenseCategory)

async def get_expenses_service(
        repo: ExpenseRepository = Depends(get_expenses_repository)
) -> ExpenseService:
    return ExpenseService(repo)
