import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, model_validator

# from src.base.filters import OperationFilterBase

class GroupedOperation(BaseModel):
    category_id: int
    category_name: str
    total_amount: float


class GroupedExpense(GroupedOperation):
    pass


class GroupedIncome(GroupedOperation):
    pass


class TotalOperationSum(BaseModel):
    total_sum: float | None
    categories: list[GroupedOperation]

    model_config = ConfigDict(from_attributes=True)


class TotalExpenseSum(TotalOperationSum):
    pass


class TotalIncomeSum(TotalOperationSum):
    pass


# class ReportFilter(OperationFilterBase):
#     pass
