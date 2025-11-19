from src.expenses.schemas import ExpenseCategory
from src.core.dependencies import make_category_validator

validate_category = make_category_validator(
    ExpenseCategory, "Категория расходов"
)
