import datetime as dt
from enum import Enum

from fastapi import FastAPI
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

@app.post("/income")
def create_income(income: Income):
    incomes.append(income)

    return {
        "message": "Income added",
        "data": income
    }
