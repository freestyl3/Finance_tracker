import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.base.service import BaseService
from src.accounts.repository import AccountRepository
from src.accounts.schemas import AccountCreate

class AccountService(BaseService[AccountRepository]):
    def __init__(self, repo: AccountRepository):
        super().__init__(repo)

    async def create(self, user_id: uuid.UUID, create_data: AccountCreate):
        try:
            new_account = await self.repo.create(
                account_data=create_data,
                user_id=user_id
            )
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        return new_account
