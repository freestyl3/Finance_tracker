import datetime as dt

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

expenses = []

class Expense(BaseModel):
    amount: float
    category: str
    description: str = None
    date: dt.date = Field(default_factory=dt.date.today)

@app.post('/expense')
def create_expense(expense: Expense):
    expenses.append(expense)

    return {
        "message": "Expense added",
        "data": expense
    }
