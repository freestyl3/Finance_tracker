from pydantic import BaseModel

class GroupedExpense(BaseModel):
    category_id: int
    total_amount: float
