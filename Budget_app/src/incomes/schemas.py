from enum import Enum

from pydantic import Field

from src.expenses.schemas import ExpenseBase

class IncomeCategory(str, Enum):
    salary = "Зарплата"
    gifts = "Подарки"


class Income(ExpenseBase):
    category: IncomeCategory = Field(
        max_length=50,
        description="Название категории, максимум 50 символов"
    )
