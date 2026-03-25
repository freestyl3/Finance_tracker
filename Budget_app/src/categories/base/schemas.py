import uuid
from pydantic import BaseModel, Field, ConfigDict, field_validator

from src.common.enums import OperationType

class CategoryRead(BaseModel):
    id: uuid.UUID
    name: str
    type: OperationType

    model_config = ConfigDict(from_attributes=True)


class CategoryUpdate(BaseModel):
    name: str = Field(max_length=255, description="Название категории")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v.startswith("__") and v.endswith("__"):
            raise ValueError("Names which starts and ends with '__' are reserved")
        return v


class CategoryCreate(CategoryUpdate):
    type: OperationType = Field(description="Тип категории (расход/доход)")
    
    @field_validator("type")
    @classmethod
    def validate(cls, v: OperationType) -> OperationType:
        if v not in (OperationType.INCOME, OperationType.EXPENSE):
            raise ValueError("Can't use this type to create category")
        return v


class GroupedAvailableCategories(BaseModel):
    expense_categories: list[str]
    income_categories: list[str]
