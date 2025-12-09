import datetime as dt

from pydantic import Field, ConfigDict

from src.expenses.schemas import ExpenseBase


class IncomeBase(ExpenseBase):
    amount: float = Field(
        gt=0,
        description="Сумма должна быть положительным числом"
    )
    description: str | None = Field(
        None,
        max_length=200,
        description="Необязательное описание, максимум 200 символов"
    )
    category_id: int = Field(
        description="ID категории доходов"
    )
    date: dt.date = Field(
        default_factory=dt.date.today,
        description="Дата дохода, по умолчанию - сегодня"
    )


class IncomeCreate(IncomeBase):
    pass


class IncomeRead(IncomeBase):
    id: int
    user_id: int
    created_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)


class IncomeUpdate(IncomeBase):
    amount: float | None = Field(
        None,
        gt=0,
        description="Сумма должна быть положительным числом"
    )
    description: str | None = Field(
        None,
        max_length=200,
        description="Необязательное описание, максимум 200 символов"
    )
    category_id: int | None = Field(
        None,
        description="ID категории доходов"
    )
    date: dt.date | None = Field(
        None,
        description="Дата дохода"
    )
