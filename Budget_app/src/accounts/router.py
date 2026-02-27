from typing import List
import uuid

from fastapi import APIRouter

from src.accounts.dependencies import AccountServiceDep
from src.accounts.schemas import AccountRead, AccountCreate, AccountUpdate
from src.auth.dependencies import CurrentUser
from src.auth.models import User

router = APIRouter()

@router.post("/", response_model=AccountRead)
async def create_account(
    account: AccountCreate,
    service: AccountServiceDep,
    current_user: CurrentUser
):
    return await service.create(current_user.id, account)

@router.get("/", response_model=List[AccountRead])
async def get_active_accounts(
    service: AccountServiceDep,
    current_user: CurrentUser
):
    return await service.get_all(current_user.id, only_active=True)

@router.put("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: uuid.UUID,
    account_update: AccountUpdate,
    service: AccountServiceDep,
    current_user: CurrentUser
):
    return await service.update(account_id, account_update, current_user.id)

@router.delete("/{account_id}")
async def soft_delete_account(
    account_id: uuid.UUID,
    service: AccountServiceDep,
    current_user: CurrentUser
):
    return await service.soft_delete(account_id, current_user.id)
