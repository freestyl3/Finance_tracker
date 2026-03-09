import datetime as dt
import uuid
from typing import Any

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field, model_validator, field_validator

from src.common.enums import OperationType
from src.operations.models import Operation            

class OperationFilter(Filter):
    categories: list[uuid.UUID] | None = Field(None, description="Фильтр по категории")
    type: OperationType | None = Field(None, description="Фильтр по типу операции")
    accounts: list[uuid.UUID] | None = Field(None, description="Фильтр по счетам")
    date_from: dt.date | None = Field(None, description="Начиная с этой даты")
    date_to: dt.date | None = Field(None, description="По эту дату включительно")

    class Constants(Filter.Constants):
        model = Operation

    @field_validator("categories", "accounts", mode="before")
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