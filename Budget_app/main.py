from fastapi import FastAPI

from src.expenses.router import router as expenses_router
from src.incomes.router import router as incomes_router
from src.reports.router import router as reports_router
from src.auth.router import router as auth_router

app = FastAPI()

app.include_router(expenses_router, prefix="/expenses", tags=["expenses"])
app.include_router(incomes_router, prefix="/incomes", tags=["incomes"])
app.include_router(reports_router, prefix="/reports", tags=["reports"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
def root():
    return {"message": "Budget API"}
