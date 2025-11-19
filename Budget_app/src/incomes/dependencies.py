from src.incomes.schemas import IncomeCategory
from src.core.dependencies import make_category_validator

validate_category = make_category_validator(
    IncomeCategory, "Категория доходов"
)
