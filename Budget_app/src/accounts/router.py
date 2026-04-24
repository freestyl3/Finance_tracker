import uuid

from fastapi import APIRouter, Response, Query

from src.accounts.dependencies import AccountServiceDep
from src.accounts.schemas import AccountRead, AccountCreate, AccountUpdate
from src.auth.dependencies import CurrentUserID

router = APIRouter()

@router.post("/check_before_creation", response_model=list[AccountRead])
async def check_before_creation(
    account: AccountCreate,
    service: AccountServiceDep,
    user_id: CurrentUserID
):
    return await service.check_deleted(
        create_data=account,
        user_id=user_id
    ) or Response(status_code=404)

@router.patch("/restore/{account_id}", response_model=AccountRead)
async def restore_account(
    account_id: uuid.UUID,
    service: AccountServiceDep,
    user_id: CurrentUserID
):
    return await service.restore(account_id, user_id)

@router.post("/", response_model=AccountRead)
async def create_account(
    account: AccountCreate,
    service: AccountServiceDep,
    user_id: CurrentUserID
):
    return await service.create(account, user_id)

@router.get("/", response_model=list[AccountRead])
async def get_accounts(
    service: AccountServiceDep,
    user_id: CurrentUserID,
    active: bool = Query(...)
):
    return await service.get_all(user_id, is_active=active)

@router.patch("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: uuid.UUID,
    account_update: AccountUpdate,
    service: AccountServiceDep,
    user_id: CurrentUserID
):
    return await service.update(account_id, account_update, user_id)

@router.delete("/{account_id}")
async def delete_account(
    account_id: uuid.UUID,
    service: AccountServiceDep,
    user_id: CurrentUserID
):
    await service.delete(account_id, user_id)
    return Response(status_code=204)
