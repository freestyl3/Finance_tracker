from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.exc import IntegrityError

from src.incomes.schemas import IncomeCreate, IncomeRead, IncomeUpdate
from src.incomes.repository import IncomeRepository
from src.incomes.dependencies import get_incomes_repository
from src.auth.dependencies import get_current_user
from src.auth.models import User

router = APIRouter()

@router.post("/", response_model=IncomeRead)
async def add_income(
    income: IncomeCreate,
    repo: IncomeRepository = Depends(get_incomes_repository),
    current_user: User = Depends(get_current_user)
):
    is_valid_category = await repo.check_category_owner(
        income.category_id,
        user_id=current_user.id
    )

    if not is_valid_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found."
        )
    
    new_income = await repo.create_income(
        income_data=income,
        user_id=current_user.id
    )
    
    return new_income

@router.get("/", response_model=list[IncomeRead])
async def get_incomes(
    repo: IncomeRepository = Depends(get_incomes_repository),
    current_user: User = Depends(get_current_user)
):
    return await repo.get_incomes(current_user.id)


@router.delete("/{income_id}")
async def delete_income(
    income_id: int,
    repo: IncomeRepository = Depends(get_incomes_repository),
    current_user: User = Depends(get_current_user)
):
    is_deleted = await repo.delete_income(income_id, current_user.id)

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
    current_user: User = Depends(get_current_user)
):
    if income_update.category_id:
        is_valid_category = await repo.check_category_owner(
            income_update.category_id,
            current_user.id
        )

        if not is_valid_category:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found."
        )

    updated_income = await repo.update_income(
        income_id,
        current_user.id,
        income_update
    )

    if not updated_income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income not found or you don't have permission."
        )
    
    return updated_income
