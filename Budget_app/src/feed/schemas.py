import uuid
from typing import Annotated, Literal, Union
from decimal import Decimal
import datetime as dt

from pydantic import BaseModel, ConfigDict, Field

from src.accounts.schemas import AccountRead
from src.categories.base.schemas import CategoryRead

class FeedItemBase(BaseModel):
    id: uuid.UUID
    amount: Decimal
    date: dt.date
    description: str | None
    ignore: bool
    account: AccountRead 
    category: CategoryRead | None 

    model_config = ConfigDict(from_attributes=True)

class FeedOperation(FeedItemBase):
    entry_type: Literal["operation"] = "operation"

class FeedChain(FeedItemBase):
    entry_type: Literal["chain"] = "chain"
    operations_count: int

FeedItem = Annotated[Union[FeedOperation, FeedChain], Field(discriminator="entry_type")]

class FeedResponse(BaseModel):
    items: list[FeedItem]
    next_month: int | None
    next_year: int | None
    has_more: bool