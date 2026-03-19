import uuid
from decimal import Decimal
import datetime as dt
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, ConfigDict

from src.common.enums import OperationType
from src.accounts.schemas import AccountRead
from src.operations.schemas import OperationDateAmountValidator
from src.categories.base.schemas import CategoryRead
from src.operations.schemas import OperationInChainRead

if TYPE_CHECKING:
    from src.accounts.models import Account
    from src.operations.models import Operation


@dataclass
class ChainMetadata():
    total_amount: Decimal
    account: "Account"
    operations: list["Operation"]
    suggested_type: OperationType | None


class ChainCreate(BaseModel, OperationDateAmountValidator):
    operation_uuids: list[uuid.UUID] = Field(description="Список ID операций")
    category_id: uuid.UUID = Field(description="ID категории")
    date: dt.date | None = Field(description="Дата цепочки")
    description: str | None = Field(None, description="Необязательное описание")


class ChainShortRead(BaseModel):
    id: uuid.UUID
    amount: Decimal
    category: CategoryRead | None =Field(None)
    ignore: bool
    date: dt.date
    description: str | None = Field(None)
    account: AccountRead
    operations_count: int

    model_config = ConfigDict(from_attributes=True)


class ChainDetailRead(ChainShortRead):
    operations: list[OperationInChainRead]
