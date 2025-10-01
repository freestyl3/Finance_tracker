import datetime as dt

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

expenses = []

class Expense(BaseModel):
    amount: float = Field(gt=0)
    category: str = Field(max_length=50)
    description: str | None = Field(None, max_length=200)
    date: dt.date = Field(default_factory=dt.date.today)

@app.post("/expense")
def create_expense(expense: Expense):
    expenses.append(expense)

    return {
        "message": "Expense added",
        "data": expense
    }
