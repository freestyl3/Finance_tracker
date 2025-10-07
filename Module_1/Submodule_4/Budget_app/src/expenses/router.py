from typing import List

from fastapi import APIRouter, Depends

from .schemas import Expense
from .dependencies import validate_category
from ..auth.dependencies import ensure_user_active

router = APIRouter()
expenses: List[Expense] = []

@router.post("/", response_model=Expense)
def add_expense(expense: Expense):
    expenses.append(expense)
    return expense

@router.get("/")
def get_expenses(category: str | None = Depends(validate_category)):

    if category is None:
        if expenses:
            return {
                "expenses": {
                    "total": sum(expense.amount for expense in expenses),
                    "data": expenses
                }
            }
        return {"message": "No expenses added"}
    
    sorted_expenses = [
        expense for expense in expenses if expense.category == category
    ]

    return {
        "expenses": {
            "category": category,
            "total": sum([expense.amount for expense in sorted_expenses]),
            "data": sorted_expenses
        }
    }
