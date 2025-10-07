from .schemas import ExpenseCategory
from ..core.dependencies import make_category_validator

validate_category = make_category_validator(
    ExpenseCategory, "Категория расходов"
)
