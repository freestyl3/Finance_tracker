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
    incomes: CategoryWithTotal
    expenses: CategoryWithTotal
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
