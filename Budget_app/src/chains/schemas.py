import uuid
from decimal import Decimal
import datetime as dt

from pydantic import BaseModel, Field, ConfigDict

from src.common.enums import OperationType
from src.accounts.schemas import AccountRead
from src.categories.user_categories.models import UserCategory
from src.operations.schemas import OperationDateAmountValidator
from src.categories.base.schemas import CategoryRead

class ChainPreview(BaseModel):
    operation_uuids: list[uuid.UUID] = Field(description="Список ID операций")


class ChainPreviewResponse(BaseModel):
    can_create: bool
    operations_count: int | None = Field(None)
    operations_sum: Decimal | None = Field(None)
    allowed_category_type: OperationType | None = Field(None)
    account: AccountRead | None = Field(None)
    operation_uuids: list[uuid.UUID] | None = Field(None)
    error_message: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)


class ChainCreate(ChainPreview):
    category_id: uuid.UUID = Field(description="ID категории")
    date: dt.date | None = Field(description="Дата цепочки")
    description: str | None = Field(None, description="Необязательное описание")


class ChainRead(BaseModel, OperationDateAmountValidator):
    id: uuid.UUID
    amount: Decimal
    category: CategoryRead | None =Field(None)
    ignore: bool
    date: dt.date
    description: str | None = Field(None)
    account: AccountRead

    model_config = ConfigDict(from_attributes=True)
