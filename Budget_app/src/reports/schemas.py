import datetime as dt

from pydantic import BaseModel, ConfigDict

from src.categories.base.schemas import CategoryRead

class GroupedCategory(BaseModel):
    category: CategoryRead
    amount: float
    
    model_config = ConfigDict(from_attributes=True)
    
class CategoryWithTotal(BaseModel):
    categories: list[GroupedCategory]
    total_amount: float

class ReportResponse(BaseModel):
    date_from: dt.date
    date_to: dt.date
    incomes: CategoryWithTotal
    expenses: CategoryWithTotal
    next_start: dt.date | None
    next_end: dt.date | None
    has_more: bool
    
# {
#   "incomes": {
#      "categories": {
#          [
#              "id": id,
#              "name": name,
#              "amount": float
#          ]
#      },
#      "total_amount": float
#    }
# }
