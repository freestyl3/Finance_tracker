from fastapi import APIRouter

from src.expenses.router import expenses, get_expenses
from src.incomes.router import incomes, get_incomes

router = APIRouter()

@router.get("/difference")
def get_difference():
    incomes_sum = sum([income.amount for income in incomes])
    expenses_sum = sum([expense.amount for expense in expenses])

    return {
        **get_incomes(None),
        **get_expenses(None),
        "difference": incomes_sum - expenses_sum
    }
