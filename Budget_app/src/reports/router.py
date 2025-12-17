from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from src.reports.schemas import TotalExpenseSum, ReportFilter
from src.expenses.repository import ExpenseRepository
from src.expenses.dependencies import get_expenses_repository
from src.auth.models import User
from src.auth.dependencies import get_current_user
from src.reports.utils import generate_csv_report

router = APIRouter()

@router.get("/expenses", response_model=TotalExpenseSum)
async def get_expenses_by_categories(
    filters: ReportFilter = Depends(),
    current_user: User = Depends(get_current_user),
    repo: ExpenseRepository = Depends(get_expenses_repository)
):
    try:
        filters.check_date_order()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return await repo.get_expenses_stats(
        user_id=current_user.id,
        filter_params=filters
    )

@router.get("/expenses/export")
async def get_expenses_by_categories(
    filters: ReportFilter = Depends(),
    current_user: User = Depends(get_current_user),
    repo: ExpenseRepository = Depends(get_expenses_repository)
):
    try:
        filters.check_date_order()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    report_data = await repo.get_expenses_stats(
        user_id=current_user.id,
        filter_params=filters
    )

    csv_file = generate_csv_report(report_data)

    filename = f"report_{filters.date_from or "all"}_{filters.date_to or "all"}.csv"

    return StreamingResponse(
        iter([csv_file.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# @router.get("/difference")
# def get_difference():
#     incomes_sum = sum([income.amount for income in incomes])
#     expenses_sum = sum([expense.amount for expense in expenses])

#     return {
#         **get_incomes(None),
#         **get_expenses(None),
#         "difference": incomes_sum - expenses_sum
#     }
