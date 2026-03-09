import datetime as dt
import uuid
from decimal import Decimal

from pydantic import Field, field_validator, BaseModel, ConfigDict, ValidationInfo

from src.common.enums import OperationType
from src.categories.base.schemas import CategoryRead
from src.accounts.schemas import AccountRead

class OperationDateAmountValidator:
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
    
    ### Переписать на model_validator
    # @field_validator("amount", mode="after")
    # @classmethod
    # def validate_amount(cls, v: float, info: ValidationInfo) -> float:
    #     return -v if info.data.get("type") == OperationType.EXPENSE else v
    
    ## Добавить в model_validator валидацию типа операции и категории и удалить логику из сервиса


class OperationBase(BaseModel):
    amount: Decimal = Field(
        description="Сумма должна быть положительным числом",
        gt=0
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
    

class OperationCreate(OperationBase, OperationDateAmountValidator):
    category_id: uuid.UUID = Field(
        description="ID категории операции"
    )
    account_id: uuid.UUID = Field(
        description="ID счета"
    )


class OperationRead(OperationBase):
    id: uuid.UUID
    amount: Decimal
    category: CategoryRead
    account: AccountRead

    model_config = ConfigDict(from_attributes=True)


class OperationUpdate(BaseModel, OperationDateAmountValidator):
    amount: Decimal | None = Field(
        None,
        gt=0,
        description="Сумма должна быть положительным числом"
    )
    description: str | None = Field(
        None,
        max_length=200,
        description="Необязательное описание, максимум 200 символов"
    )
    category_id: uuid.UUID | None = Field(
        None,
        description="ID категории операции"
    )
    date: dt.date | None = Field(
        None,
        description="Дата операции"
    )
    account_id: uuid.UUID | None = Field(
        None,
        description="ID счета"
    )
