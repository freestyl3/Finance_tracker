import datetime as dt
import uuid
from decimal import Decimal

from pydantic import Field, BaseModel

from src.operations.schemas import (
    OperationBase, OperationDateValidator, OperationRead
)

class TransferCreate(OperationBase, OperationDateValidator):
    account_from: uuid.UUID = Field(
        description="ID счета, с которого уходит перевод"
    )
    account_to: uuid.UUID = Field(
        description="ID счета, на который приходит перевод"
    )


class TransferResponse(BaseModel):
    withdrawal: OperationRead
    deposit: OperationRead


class TransferUpdate(BaseModel, OperationDateValidator):
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
    date: dt.date | None = Field(
        None,
        description="Дата операции"
    )
    account_from_id: uuid.UUID | None = Field(
        None,
        description="ID счета, с которого уходит перевод"
    )
    account_to_id: uuid.UUID | None = Field(
        None,
        description="ID счета, на который приходит перевод"
    )