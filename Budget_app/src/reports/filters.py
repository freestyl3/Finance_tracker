import datetime as dt

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field, model_validator

from src.feed.models import FeedItemORM

class ReportFilter(Filter):
    date_from: dt.date | None = Field(None, description="Начиная с этой даты")
    date_to: dt.date | None = Field(None, description="По эту дату включительно")

    class Constants(Filter.Constants):
        model = FeedItemORM

    @model_validator(mode='after')
    def check_date_order(self):
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValueError("The start date cannot be later than the end date.")
            
        return self