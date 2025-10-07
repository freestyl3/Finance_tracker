from .schemas import IncomeCategory
from ..core.dependencies import make_category_validator

validate_category = make_category_validator(
    IncomeCategory, "Категория доходов"
)
