from typing import List

from fastapi import APIRouter, Depends

from src.expenses.schemas import ExpenseCreate, ExpenseRead
from src.expenses.dependencies import get_expenses_repository
from src.auth.dependencies import ensure_user_active
from src.expenses.repository import ExpenseRepository

router = APIRouter()
# expenses: List[Expense] = []

@router.post("/", response_model=ExpenseRead)
async def add_expense(
    expense_data: ExpenseCreate, 
    repo: ExpenseRepository = Depends(get_expenses_repository),
    user_username: str = Depends(ensure_user_active)
):
    current_user_id = 1

    new_expense = await repo.create_expense(
        expense_data=expense_data,
        user_id=current_user_id
    )

    return new_expense

@router.get("/", response_model=List[ExpenseRead])
async def get_expenses(
    repo: ExpenseRepository = Depends(get_expenses_repository),
    user_username: str = Depends(ensure_user_active)
):
    current_user_id = 1
    expenses = await repo.get_expenses(current_user_id)

    return expenses
