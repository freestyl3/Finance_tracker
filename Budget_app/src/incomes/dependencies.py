from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# from src.incomes.schemas import IncomeCategory
from src.core.dependencies import make_category_validator
from src.incomes.repository import IncomeRepository
from src.database.db_helper import db_helper

# validate_category = make_category_validator(
#     IncomeCategory, "Категория доходов"
# )

async def get_incomes_repository(
    session: AsyncSession = Depends(db_helper.session_dependency)
) -> IncomeRepository:
    return IncomeRepository(session)
