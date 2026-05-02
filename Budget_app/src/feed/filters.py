import datetime as dt
import uuid
from typing import Any

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field, model_validator, field_validator

from src.common.enums import OperationType
from src.feed.models import FeedItemORM

class FeedFilter(Filter):
    date_from: dt.date | None = Field(None, description="Начиная с этой даты")
    date_to: dt.date | None = Field(None, description="По эту дату включительно")

    account_ids: list[uuid.UUID] | None = Field(None, description="Фильтр по счетам")

    type: OperationType | None = Field(None, description="Фильтр по типу операции")
    category_ids: list[uuid.UUID] | None = Field(None, description="Фильтр по категории")
    category_inside_chains: bool = Field(False, description="Искать категории внутри цепочек")

    search_query: str | None = Field(None, description="Поиск по описанию")

    limit: int = Field(100, ge=1, le=100, description="Количество записей")
    cursor_date: dt.date | None = Field(None, description="Дата последнего элемента с прошлой страницы")
    cursor_id: uuid.UUID | None = Field(None, description="ID последнего элемента с прошлой страницы")

    class Constants(Filter.Constants):
        model = FeedItemORM

    @field_validator("category_ids", "account_ids", mode="before")
    @classmethod
    def split_comma_separated_string(cls, v: Any) -> Any:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @model_validator(mode='after')
    def check_date_order(self):
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValueError("The start date cannot be later than the end date.")
            
        return self
