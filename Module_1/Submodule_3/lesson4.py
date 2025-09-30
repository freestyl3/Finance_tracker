import datetime as dt

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

expenses = []

class Expense(BaseModel):
    amount: float = Field(
        gt=0,
        description="Сумма должна быть положительным числом"
    )
    category: str = Field(
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

@app.post('/expense')
def create_expense(expense: Expense):
    expenses.append(expense)

    return {
        "message": "Expense added",
        "data": expense
    }
