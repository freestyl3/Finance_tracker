import uuid
from pydantic import BaseModel, Field

from src.operations.models import OperationType

class CategoryRead(BaseModel):
    id: uuid.UUID
    name: str
    type: OperationType


class CategoryCreate(BaseModel):
    name: str = Field(max_length=255, description="Название категории")
    type: OperationType = Field(description="Тип категории (расход/доход)")


class CategoryUpdate(BaseModel):
    name: str = Field(max_length=255, description="Название категории")
