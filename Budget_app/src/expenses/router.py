from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from src.expenses.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate
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

    try:
        new_expense = await repo.create_expense(
            expense_data=expense_data,
            user_id=current_user_id
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category_id. Category does not exist."
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

@router.delete("/{expense_id}")
async def delete_exepense(
        expense_id: int,
        repo: ExpenseRepository = Depends(get_expenses_repository),
        user_username: str = Depends(ensure_user_active)
):
    current_user_id = 1

    is_deleted = await repo.delete_expense(expense_id, current_user_id)

    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found or you don't have permission."
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{expense_id}", response_model=ExpenseRead)
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    repo: ExpenseRepository = Depends(get_expenses_repository),
    user_username: str = Depends(ensure_user_active)
):
    current_user_id = 1

    updated_expense = await repo.update_expense(
        expense_id,
        current_user_id,
        expense_update
    )

    if not updated_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found or you don't have permission."
        )
    
    return updated_expense