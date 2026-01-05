from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# from src.incomes.schemas import IncomeCategory
from src.core.dependencies import make_category_validator
from src.operations.incomes.repository import IncomeRepository
from src.database.db_helper import db_helper
from src.operations.incomes.service import IncomeService
from src.operations.incomes.models import Income, IncomeCategory

async def get_incomes_repository(
    session: AsyncSession = Depends(db_helper.session_dependency)
) -> IncomeRepository:
    return IncomeRepository(session, Income, IncomeCategory)

async def get_incomes_service(
    repo: IncomeRepository = Depends(get_incomes_repository)
):
    return IncomeService(repo)
