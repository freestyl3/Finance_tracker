from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.exc import IntegrityError

from src.operations.incomes.schemas import IncomeCreate, IncomeRead, IncomeUpdate, IncomeFilter
from src.operations.incomes.repository import IncomeRepository
from src.operations.incomes.dependencies import get_incomes_repository, get_incomes_service
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.operations.incomes.service import IncomeService
from src.pagination import PaginationParams

router = APIRouter()

### Переписать обработку категории пользователя внутрь репозитория 
### Сделать зависимости для пагинации

@router.post("/", response_model=IncomeRead)
async def add_income(
    income: IncomeCreate,
    service: IncomeService = Depends(get_incomes_service),
    current_user: User = Depends(get_current_user)
):
    return await service.create(current_user.id, income)

@router.get("/", response_model=list[IncomeRead])
async def get_incomes(
    filters: Annotated[IncomeFilter, Query()],
    current_user: User = Depends(get_current_user),
    pagination: PaginationParams = Depends(),
    service: IncomeService = Depends(get_incomes_service)
):
    return await service.get_all(current_user.id, filters, pagination)

@router.put("/{income_id}", response_model=IncomeRead)
async def update_income(
    income_id: int,
    income_update: IncomeUpdate,
    current_user: User = Depends(get_current_user),
    service: IncomeService = Depends(get_incomes_service)
):  
    return await service.update(income_id, income_update, current_user.id)

@router.delete("/{income_id}")
async def delete_exepense(
        income_id: int,
        current_user: User = Depends(get_current_user),
        service: IncomeService = Depends(get_incomes_service)
):
    return await service.delete(income_id, current_user.id)
