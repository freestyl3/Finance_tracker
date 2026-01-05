from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse

from src.reports.schemas import TotalExpenseSum, ReportFilter
from src.operations.expenses.service import ExpenseService
from src.operations.expenses.dependencies import get_expenses_service
from src.operations.incomes.dependencies import get_incomes_service
from src.auth.models import User
from src.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/expenses", response_model=TotalExpenseSum)
async def get_expenses_by_categories(
    filters: ReportFilter = Depends(),
    current_user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expenses_service)
):
    return await service.get_operations_stats(
        user_id=current_user.id,
        filter_params=filters
    )

@router.get("/expenses/export")
async def get_expenses_report(
    filters: ReportFilter = Depends(),
    current_user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expenses_service)
):
    csv_file , filename = service.get_operations_report(
        current_user.id,
        filters
    )

    return StreamingResponse(
        iter([csv_file.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/expenses/monthly", response_model=TotalExpenseSum)
async def get_monthly_expenses(
    year: int | None = Query(None, ge=2000, le=date.today().year),
    month: int | None = Query(None, ge=1, le=12),

    current_user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expenses_service)
):
    return await service.get_monthly_operations(year, month, current_user.id)

# @router.get("/difference")
# def get_difference():
#     incomes_sum = sum([income.amount for income in incomes])
#     expenses_sum = sum([expense.amount for expense in expenses])

#     return {
#         **get_incomes(None),
#         **get_expenses(None),
#         "difference": incomes_sum - expenses_sum
#     }
