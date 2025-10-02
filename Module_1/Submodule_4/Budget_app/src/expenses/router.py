from typing import List

from fastapi import APIRouter, HTTPException, status, Query
from .schemas import Expense, ExpenseCategory

router = APIRouter()
expenses: List[Expense] = []

@router.post("/", response_model=Expense)
def add_expense(expense: Expense):
    expenses.append(expense)
    return expense

@router.get("/")
def get_expenses(
        category: str | None= Query(None, description="Категория расхода")
    ):

    if category is None:
        if expenses:
            return {
                "expenses": {
                    "total": sum(expense.amount for expense in expenses),
                    "data": expenses
                }
            }
        return {"message": "No expenses added"}

    try:
        category_enum = ExpenseCategory(category)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Category {category} does not exists",
                "available_categories": [
                    category.value for category in ExpenseCategory
                ]
            }
        )
    
    sorted_expenses = [
        expense for expense in expenses if expense.category == category_enum
    ]

    return {
        "expenses": {
            "category": category,
            "total": sum([expense.amount for expense in sorted_expenses]),
            "data": sorted_expenses
        }
    }

