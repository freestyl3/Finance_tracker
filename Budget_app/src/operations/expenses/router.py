from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from sqlalchemy.exc import IntegrityError

from src.operations.expenses.schemas import (
    ExpenseCreate, ExpenseRead, ExpenseUpdate, ExpenseFilter
)
from src.operations.expenses.dependencies import get_expenses_repository, get_expenses_service
from src.auth.dependencies import get_current_user
from src.operations.expenses.repository import ExpenseRepository
from src.operations.expenses.service import ExpenseService
from src.auth.models import User
from src.pagination import PaginationParams
from src.operations.expenses.service import ExpenseService

router = APIRouter()

### Переписать обработку категории пользователя внутрь репозитория 
### Сделать зависимости для пагинации

@router.post("/", response_model=ExpenseRead)
async def add_expense(
    expense: ExpenseCreate,
    service: ExpenseService = Depends(get_expenses_service),
    current_user: User = Depends(get_current_user)
):
    return await service.create(current_user.id, expense)

@router.get("/", response_model=List[ExpenseRead])
async def get_expenses(
    filters: Annotated[ExpenseFilter, Query()],
    current_user: User = Depends(get_current_user),
    pagination: PaginationParams = Depends(),
    service: ExpenseService = Depends(get_expenses_service)
):
    return await service.get_all(current_user.id, filters, pagination)

@router.put("/{expense_id}", response_model=ExpenseRead)
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expenses_service)
):  
    return await service.update(expense_id, expense_update, current_user.id)

@router.delete("/{expense_id}")
async def delete_exepense(
        expense_id: int,
        current_user: User = Depends(get_current_user),
        service: ExpenseService = Depends(get_expenses_service)
):
    return await service.delete(expense_id, current_user.id)
