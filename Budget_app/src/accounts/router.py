from typing import List

from fastapi import APIRouter, Depends

from src.accounts.dependencies import get_accounts_service
from src.accounts.service import AccountService
from src.accounts.schemas import AccountRead, AccountCreate
from src.auth.dependencies import get_current_user
from src.auth.models import User

router = APIRouter()

@router.post("/", response_model=AccountRead)
async def create_account(
    account: AccountCreate,
    service: AccountService = Depends(get_accounts_service),
    current_user: User = Depends(get_current_user)
):
    return await service.create(current_user.id, account)

@router.get("/", response_model=List[AccountRead])
async def get_accounts(
    service: AccountService = Depends(get_accounts_service),
    current_user: User = Depends(get_current_user)
):
    return await service.get_all(current_user.id)