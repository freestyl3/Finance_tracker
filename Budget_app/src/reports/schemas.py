from pydantic import BaseModel, ConfigDict

class GroupedExpense(BaseModel):
    category_id: int
    total_amount: float


class TotalExpenseSum(BaseModel):
    total_sum: float | None
    categories: list[GroupedExpense]

    model_config = ConfigDict(from_attributes=True)
