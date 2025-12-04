from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# from src.expenses.schemas import ExpenseCategory
from src.expenses.repository import ExpenseRepository
from src.core.dependencies import make_category_validator
from src.database.db_helper import db_helper

# validate_category = make_category_validator(
#     ExpenseCategory, "Категория расходов"
# )

async def get_expenses_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> ExpenseRepository:
    return ExpenseRepository(session)
