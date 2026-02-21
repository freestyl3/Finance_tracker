import datetime as dt

from pydantic import Field, field_validator, BaseModel, ConfigDict

class CategoryRead(BaseModel):
    id: int
    name: str
    can_disable: bool

    model_config = ConfigDict(from_attributes=True)

class OperationDateValidator:
    @field_validator("date")
    @classmethod
    def validate_date(cls, v: dt.date | None) -> dt.date:
        if not v:
            return v
        
        if v > dt.date.today():
            raise ValueError("Дата не может быть в будущем")
        if v < dt.date(2000, 1, 1):
            raise ValueError("Дата не может быть раньше 2000 года")
        return v


class OperationBase(BaseModel):
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
        description="Дата операции, по умолчанию - сегодня"
    ) 
    

class OperationCreate(OperationBase, OperationDateValidator):
    category_id: int = Field(
        description="ID категории операции"
    )


class OperationRead(OperationBase):
    id: int
    user_id: int
    created_at: dt.datetime
    category: CategoryRead

    model_config = ConfigDict(from_attributes=True)


class OperationUpdate(OperationBase, OperationDateValidator):
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
        description="ID категории операции"
    )
    date: dt.date | None = Field(
        None,
        description="Дата операции"
    )