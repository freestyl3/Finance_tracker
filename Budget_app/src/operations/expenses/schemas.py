import datetime as dt

from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator

from src.base.schemas import (
    OperationBase, OperationCreate, OperationRead,
    OperationUpdate, CategoryRead
)
from src.base.filters import OperationFilterBase

class ExpenseCategoryRead(CategoryRead):
    pass


class ExpenseBase(OperationBase):
    pass
    

class ExpenseCreate(OperationCreate):
    pass


class ExpenseRead(OperationRead):
    pass


class ExpenseUpdate(OperationUpdate):
    pass


class ExpenseFilter(OperationFilterBase):
    pass
