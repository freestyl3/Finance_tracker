from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from src.expenses.schemas import (
    ExpenseCreate, ExpenseRead, ExpenseUpdate, ExpenseFilter
)
from src.expenses.dependencies import get_expenses_repository
from src.auth.dependencies import get_current_user
from src.expenses.repository import ExpenseRepository
from src.auth.models import User

router = APIRouter()

@router.post("/", response_model=ExpenseRead)
async def add_expense(
    expense: ExpenseCreate, 
    repo: ExpenseRepository = Depends(get_expenses_repository),
    current_user: User = Depends(get_current_user)
):
    is_valid_category = await repo.check_category_owner(
        expense.category_id,
        user_id=current_user.id
    )

    if not is_valid_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found."
        )
    
    new_expense = await repo.create_expense(
        expense_data=expense,
        user_id=current_user.id
    )

    return new_expense

@router.get("/", response_model=List[ExpenseRead])
async def get_expenses(
    filters: ExpenseFilter = Depends(),
    repo: ExpenseRepository = Depends(get_expenses_repository),
    current_user: User = Depends(get_current_user)
):
    try:
        filters.check_date_order()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return await repo.get_expenses(current_user.id, filter_params=filters)

@router.delete("/{expense_id}")
async def delete_exepense(
        expense_id: int,
        repo: ExpenseRepository = Depends(get_expenses_repository),
        current_user: User = Depends(get_current_user)
):
    is_deleted = await repo.delete_expense(expense_id, current_user.id)

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
    current_user: User = Depends(get_current_user)
):
    if expense_update.category_id:
        is_valid_category = await repo.check_category_owner(
            expense_update.category_id,
            current_user.id
        )

        if not is_valid_category:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found."
        )

    updated_expense = await repo.update_expense(
        expense_id,
        current_user.id,
        expense_update
    )

    if not updated_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found or you don't have permission."
        )
    
    return updated_expense