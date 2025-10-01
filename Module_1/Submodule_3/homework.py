import datetime as dt
from enum import Enum

from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field, field_validator

app = FastAPI()

expenses = []
incomes = []

class ExpenseCategory(str, Enum):
    food = "Еда"
    transport = "Транспорт"
    fun = "Развлечения"

class IncomeCategory(str, Enum):
    salary = "Зарплата"
    gifts = "Подарки"

class Expense(BaseModel):
    amount: float = Field(
        gt=0,
        description="Сумма должна быть положительным числом"
    )
    category: ExpenseCategory = Field(
        max_length=50,
        description="Название категории, максимум 50 символов"
    )
    description: str | None = Field(
        None,
        max_length=200,
        description="Необязательное описание, максимум 200 символов"
    )
    date: dt.date = Field(
        default_factory=dt.date.today,
        description="Дата расхода, по умолчанию - сегодня"
    )

    @field_validator("date")
    def validate_date(cls, v):
        if v > dt.date.today():
            raise ValueError("Дата не может быть в будущем")
        if v < dt.date(2000, 1, 1):
            raise ValueError("Дата не может быть раньше 2000 года")
        return v
    
class Income(Expense):
    category: IncomeCategory = Field(
        max_length=50,
        description="Название категории, максимум 50 символов"
    )

@app.post("/expense")
def create_expense(expense: Expense):
    expenses.append(expense)

    return {
        "message": "Expense added",
        "data": expense
    }

@app.get("/expenses")
def get_expenses_by_category(
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

@app.post("/income")
def create_income(income: Income):
    incomes.append(income)

    return {
        "message": "Income added",
        "data": income
    }

@app.get("/incomes")
def get_incomes_by_category(
        category: str | None= Query(None, description="Категория дохода")
    ):

    if category is None:
        if incomes:
            return {
                "incomes": {
                    "total": sum([income.amount for income in incomes]),
                    "data": incomes
                }
            }
        return {"message": "No incomes added"}

    try:
        category_enum = IncomeCategory(category)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Category {category} does not exists",
                "available_categories": [
                    category.value for category in IncomeCategory
                ]
            }
        )
    
    sorted_incomes = [
        income for income in incomes if income.category == category_enum
    ]

    return {
        "incomes": {
            "category": category,
            "total": sum([income.amount for income in sorted_incomes]),
            "data": sorted_incomes
        }
    }

@app.get("/difference")
def get_difference():
    incomes_sum = sum([income.amount for income in incomes])
    expenses_sum = sum([expense.amount for expense in expenses])

    return {
        **get_incomes_by_category(None),
        **get_expenses_by_category(None),
        "difference": incomes_sum - expenses_sum
    }
