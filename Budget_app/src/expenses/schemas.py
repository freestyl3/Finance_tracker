import datetime as dt

from pydantic import BaseModel, Field, field_validator, ConfigDict

class ExpenseBase(BaseModel):
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
        description="ID категории расходов"
    )
    date: dt.date = Field(
        default_factory=dt.date.today,
        description="Дата расхода, по умолчанию - сегодня"
    )

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: dt.date) -> dt.date:
        if v > dt.date.today():
            raise ValueError("Дата не может быть в будущем")
        if v < dt.date(2000, 1, 1):
            raise ValueError("Дата не может быть раньше 2000 года")
        return v
    

class ExpenseCreate(ExpenseBase):
    pass


class ExpenseRead(ExpenseBase):
    id: int
    user_id: int
    created_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)
