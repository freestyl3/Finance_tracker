from fastapi import FastAPI

# from src.operations.expenses.router import router as expenses_router
# from src.operations.incomes.router import router as incomes_router
# from src.reports.router import router as reports_router
from src.auth.router import router as auth_router
from src.accounts.router import router as accounts_router
from src.categories.system_categories.router import router as system_categories_router
from src.categories.user_categories.router import router as user_categories_router
from src.operations.router import router as operations_router

from src.auth.models import User
from src.accounts.models import Account
from src.operations.models import Operation
# from src.operations.expenses.models import Expense, ExpenseCategory
# from src.operations.incomes.models import Income, IncomeCategory

app = FastAPI()

# app.include_router(expenses_router, prefix="/expenses", tags=["expenses"])
# app.include_router(incomes_router, prefix="/incomes", tags=["incomes"])
# app.include_router(reports_router, prefix="/reports", tags=["reports"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
app.include_router(
    system_categories_router,
    prefix="/system_categories",
    tags=["system_categories"]
)
app.include_router(
    user_categories_router,
    prefix="/categories",
    tags=["user_categories"]
)
app.include_router(operations_router, prefix="/operations", tags=["operations"])

@app.get("/")
def root():
    return {"message": "Budget API"}
