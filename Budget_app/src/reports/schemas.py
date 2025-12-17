import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.expenses.schemas import ExpenseFilter

class GroupedExpense(BaseModel):
    category_id: int
    category_name: str
    total_amount: float


class TotalExpenseSum(BaseModel):
    total_sum: float | None
    categories: list[GroupedExpense]

    model_config = ConfigDict(from_attributes=True)


class ReportFilter(ExpenseFilter):
    pass
