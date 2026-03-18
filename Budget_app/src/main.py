from fastapi import FastAPI

# from src.reports.router import router as reports_router
from src.auth.router import router as auth_router
from src.accounts.router import router as accounts_router
from src.categories.system_categories.router import router as system_categories_router
from src.categories.user_categories.router import router as user_categories_router
from src.operations.router import router as operations_router
from src.chains.router import router as chain_router

from src.auth.models import User
from src.accounts.models import Account
from src.operations.models import Operation

app = FastAPI()

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
app.include_router(
    operations_router,
    prefix="/operations",
    tags=["operations"]
)
app.include_router(chain_router, prefix="/chains", tags=["chains"])

@app.get("/")
def root():
    return {"message": "Budget API"}
