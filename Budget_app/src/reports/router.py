from fastapi import APIRouter, Depends

from src.reports.schemas import TotalExpenseSum
from src.expenses.repository import ExpenseRepository
from src.expenses.dependencies import get_expenses_repository
from src.auth.models import User
from src.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/expenses", response_model=TotalExpenseSum)
async def get_expenses_by_categories(
    current_user: User = Depends(get_current_user),
    repo: ExpenseRepository = Depends(get_expenses_repository)
):
    return await repo.get_expenses_stats(current_user.id)


# @router.get("/difference")
# def get_difference():
#     incomes_sum = sum([income.amount for income in incomes])
#     expenses_sum = sum([expense.amount for expense in expenses])

#     return {
#         **get_incomes(None),
#         **get_expenses(None),
#         "difference": incomes_sum - expenses_sum
#     }
