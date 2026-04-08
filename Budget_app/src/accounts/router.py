from typing import List
import uuid
from decimal import Decimal

from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import JSONResponse

from src.accounts.dependencies import AccountServiceDep
from src.accounts.schemas import AccountRead, AccountCreate, AccountUpdate
from src.auth.dependencies import CurrentUserID

router = APIRouter()

@router.post("/check_before_creation")
async def check_before_creation(
    account: AccountCreate,
    service: AccountServiceDep,
    user_id: CurrentUserID
):
    result = await service.check_deleted(
        create_data=account,
        user_id=user_id
    )

    if result:
        return JSONResponse(
            status_code=200,
            content={
                "account_id": str(result)
            }
        )
    return Response(
        status_code=204
    )

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
    try:
        return await service.create(account, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/", response_model=List[AccountRead])
async def get_accounts(
    service: AccountServiceDep,
    user_id: CurrentUserID
):
    return await service.get_all(user_id, only_active=False)

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
