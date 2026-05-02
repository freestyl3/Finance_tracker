from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.accounts.router import router as accounts_router
from src.categories.system_categories.router import router as system_categories_router
from src.categories.user_categories.router import router as user_categories_router
from src.operations.router import router as operations_router
from src.transfers.router import router as transfers_router
from src.chains.router import router as chain_router
from src.feed.router import router as feed_router
from src.reports.router import router as reports_router
from src.core.config import settings

from src.exception_handlers import setup_exception_handlers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.ALLOW_ORIGINS,
    allow_credentials=settings.cors.ALLOW_CREDENTIALS,
    allow_methods=settings.cors.ALLOW_METHODS,
    allow_headers=settings.cors.ALLOW_HEADERS,
)

setup_exception_handlers(app)

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
app.include_router(
    transfers_router,
    prefix="/transfers",
    tags=["transfers"]
)
app.include_router(chain_router, prefix="/chains", tags=["chains"])
app.include_router(feed_router, prefix="/feed", tags=["feed"])
app.include_router(reports_router, prefix="/reports", tags=["reports"])

@app.get("/")
def root():
    return {"message": "Budget API"}
