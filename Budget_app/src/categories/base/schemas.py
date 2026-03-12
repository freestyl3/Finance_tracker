import uuid
from pydantic import BaseModel, Field, ConfigDict

from src.common.enums import OperationType

class CategoryRead(BaseModel):
    id: uuid.UUID
    name: str
    type: OperationType

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    name: str = Field(max_length=255, description="Название категории")
    type: OperationType = Field(description="Тип категории (расход/доход)")


class CategoryUpdate(BaseModel):
    name: str = Field(max_length=255, description="Название категории")


class GroupedAvailableCategories(BaseModel):
    expense_categories: list[str] # Содержит названия категорий
    income_categories: list[str] # Содержит названия категорий
