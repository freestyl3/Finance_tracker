import datetime as dt

from pydantic import Field, model_validator, BaseModel

class OperationFilterBase(BaseModel):
    category_id: int | None = Field(None, description="Фильтр по категории")
    date_from: dt.date | None = Field(None, description="Начиная с этой даты")
    date_to: dt.date | None = Field(None, description="По эту дату включительно")

    @model_validator(mode='after')
    def check_date_order(self):
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValueError("The start date cannot be later than the end date.")
            
        return self
