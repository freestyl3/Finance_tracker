from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from fastapi_filter import FilterDepends

from src.reports.schemas import ReportResponse
from src.auth.dependencies import CurrentUserID
from src.reports.filters import ReportFilter
from src.reports.dependencies import ReportServiceDep

router = APIRouter()

@router.get("/", response_model=ReportResponse)
async def get_report(
    user_id: CurrentUserID,
    service: ReportServiceDep,
    filters: ReportFilter = FilterDepends(ReportFilter)
):
    return await service.get_report(user_id, filters)

# @router.get("/expenses", response_model=TotalExpenseSum)
# async def get_expenses_by_categories(
#     filters: ReportFilter = Depends(),
#     current_user: User = Depends(get_current_user),
#     service: ExpenseService = Depends(get_expenses_service)
# ):
#     return await service.get_operations_stats(
#         user_id=current_user.id,
#         filter_params=filters
#     )

# @router.get("/expenses/export")
# async def get_expenses_report(
#     filters: ReportFilter = Depends(),
#     current_user: User = Depends(get_current_user),
#     service: ExpenseService = Depends(get_expenses_service)
# ):
#     csv_file , filename = service.get_operations_report(
#         current_user.id,
#         filters
#     )

#     return StreamingResponse(
#         iter([csv_file.getvalue()]),
#         media_type="text/csv; charset=utf-8",
#         headers={"Content-Disposition": f"attachment; filename={filename}"}
#     )

# @router.get("/expenses/monthly", response_model=TotalExpenseSum)
# async def get_monthly_expenses(
#     year: int | None = Query(None, ge=2000, le=date.today().year),
#     month: int | None = Query(None, ge=1, le=12),

#     current_user: User = Depends(get_current_user),
#     service: ExpenseService = Depends(get_expenses_service)
# ):
#     return await service.get_monthly_operations(year, month, current_user.id)

# @router.get("/difference")
# def get_difference():
#     incomes_sum = sum([income.amount for income in incomes])
#     expenses_sum = sum([expense.amount for expense in expenses])

#     return {
#         **get_incomes(None),
#         **get_expenses(None),
#         "difference": incomes_sum - expenses_sum
#     }
