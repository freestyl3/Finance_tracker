from decimal import Decimal
import uuid
from typing import Literal

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
    name: str | None = Field(None, max_length=255, description="Новое название счета")
    balance: Decimal | None = Field(None, description="Значение баланса для корректировки")

class AccountCheckResponse(BaseModel):
    status: Literal["free", "active_exists", "archived_exists"]
    active_account: AccountRead | None = None
    archived_accounts: list[AccountRead] | None = None
