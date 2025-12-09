from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.exc import IntegrityError

from src.incomes.schemas import IncomeCreate, IncomeRead, IncomeUpdate
from src.incomes.repository import IncomeRepository
from src.incomes.dependencies import get_incomes_repository
from src.auth.dependencies import ensure_user_active
# from src.incomes.dependencies import validate_category

router = APIRouter()
# incomes: List[Income] = []

@router.post("/", response_model=IncomeRead)
async def add_income(
    income: IncomeCreate,
    repo: IncomeRepository = Depends(get_incomes_repository),
    user_username: str = Depends(ensure_user_active)
):
    current_user_id = 1

    try:
        new_income = await repo.create_income(income, current_user_id)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category_id. Category does not exist."
        )
    
    return new_income

@router.get("/", response_model=list[IncomeRead])
async def get_incomes(
    repo: IncomeRepository = Depends(get_incomes_repository),
    user_username: str = Depends(ensure_user_active)
):
    current_user_id = 1
    incomes = await repo.get_incomes(current_user_id)

    return incomes

@router.delete("/{income_id}")
async def delete_income(
    income_id: int,
    repo: IncomeRepository = Depends(get_incomes_repository),
    user_username: str = Depends(ensure_user_active)
):
    current_user_id = 1
    is_deleted = await repo.delete_income(income_id, current_user_id)

    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income not found or you don't have permission."
        )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{income_id}", response_model=IncomeRead)
async def update_income(
    income_id: int,
    income_update: IncomeUpdate,
    repo: IncomeRepository = Depends(get_incomes_repository),
    user_username: str = Depends(ensure_user_active)
):
    current_user_id = 1

    updated_income = await repo.update_income(
        income_id,
        current_user_id,
        income_update
    )

    if not updated_income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income not found or you don't have permission."
        )
    
    return updated_income
