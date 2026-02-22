from decimal import Decimal
import uuid

from pydantic import Field, ConfigDict, BaseModel

from src.accounts.models import AccountType, Currency

class AccountRead(BaseModel):
    id: uuid.UUID
    name: str
    type: AccountType
    currency: Currency
    balance: Decimal = Field(examples=[10500.50])
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class AccountCreate(BaseModel):
    name: str = Field(max_length=255, description="Название счета")
    balance: Decimal | None = Field(
        validation_alias="start_balance",
        default=0.0
    )
    type: AccountType = Field(description="Тип счета")
    currency: Currency = Field(description="Валюта счета")

class AccountUpdate(BaseModel):
    name: str = Field(max_length=255, description="Новое название счета")
