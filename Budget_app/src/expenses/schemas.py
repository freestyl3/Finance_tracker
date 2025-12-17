import datetime as dt

from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator

class ExpenseCategoryRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


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
    category_id: int = Field(
        description="ID категории расходов"
    )


class ExpenseRead(ExpenseBase):
    id: int
    user_id: int
    created_at: dt.datetime
    category: ExpenseCategoryRead

    model_config = ConfigDict(from_attributes=True)


class ExpenseUpdate(ExpenseBase):
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
        description="ID категории расходов"
    )
    date: dt.date | None = Field(
        None,
        description="Дата расхода"
    )


class ExpenseFilter(BaseModel):
    category_id: int | None = Field(None, description="Фильтр по категории")
    
    date_from: dt.date | None = Field(None, description="Начиная с этой даты")
    date_to: dt.date | None = Field(None, description="По эту дату включительно")

    limit: int = Field(50, ge=1, le=200, description="Количество записей (макс. 200)")
    offset: int = Field(0, ge=0, description="Смещение (сколько записей пропустить)")

    def check_date_order(self):
        d_from = self.date_from
        d_to = self.date_to

        if d_from and d_to:
            if d_from > d_to:
                raise ValueError("The start date cannot be later than the end date.")
            
        return self
