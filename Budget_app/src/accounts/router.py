from typing import List
import uuid
from decimal import Decimal

from fastapi import APIRouter

from src.accounts.dependencies import AccountServiceDep
from src.accounts.schemas import AccountRead, AccountCreate, AccountUpdate
from src.auth.dependencies import CurrentUserID
from src.categories.user_categories.dependecies import UserCategoryServiceDep
from src.operations.dependencies import OperationServiceDep
from src.common.enums import OperationType
from src.operations.schemas import OperationCreate

router = APIRouter()

@router.post("/", response_model=AccountRead)
async def create_account(
    account: AccountCreate,
    service: AccountServiceDep,
    user_category_service: UserCategoryServiceDep,
    operation_service: OperationServiceDep,
    user_id: CurrentUserID
):
    if account.balance:
        amount = account.balance
        account.balance = Decimal(0.0)

    account = await service.create(user_id, account)

    if amount:
        if amount > 0:
            category = await user_category_service.get_correcting_category(
                op_type=OperationType.INCOME,
                user_id=user_id
            )
        else:
            category = await user_category_service.get_correcting_category(
                op_type=OperationType.EXPENSE,
                user_id=user_id
            )

        await operation_service.create(
            OperationCreate(
                amount=abs(amount),
                description="Начальная корректировка счета",
                account_id=account.id,
                category_id=category.id
            ),
            user_id=user_id,
            system_operation=True
        )

    return account

@router.get("/", response_model=List[AccountRead])
async def get_active_accounts(
    service: AccountServiceDep,
    user_id: CurrentUserID
):
    return await service.get_all(user_id, only_active=True)

@router.put("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: uuid.UUID,
    account_update: AccountUpdate,
    service: AccountServiceDep,
    user_id: CurrentUserID
):
    return await service.update(account_id, account_update, user_id)

@router.delete("/{account_id}")
async def soft_delete_account(
    account_id: uuid.UUID,
    service: AccountServiceDep,
    user_id: CurrentUserID
):
    return await service.soft_delete(account_id, user_id)
