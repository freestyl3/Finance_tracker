import datetime as dt

from pydantic import Field, ConfigDict

from src.base.schemas import (
    OperationBase, OperationCreate, OperationRead,
    OperationUpdate, CategoryRead
)
from src.base.filters import OperationFilterBase

class IncomeCategoryRead(CategoryRead):
    pass


class IncomeBase(OperationBase):
    pass
    

class IncomeCreate(OperationCreate):
    pass


class IncomeRead(OperationRead):
    pass


class IncomeUpdate(OperationUpdate):
    pass


class IncomeFilter(OperationFilterBase):
    pass
