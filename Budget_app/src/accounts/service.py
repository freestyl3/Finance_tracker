import uuid

from fastapi import HTTPException, status, Response

from src.accounts.repository import AccountRepository
from src.accounts.schemas import AccountCreate, AccountUpdate

class AccountService:
    def __init__(self, repo: AccountRepository):
        self.repo = repo

    async def create(self, user_id: uuid.UUID, create_data: AccountCreate):
        try:
            new_account = await self.repo.create(
                account_data=create_data,
                user_id=user_id
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        return new_account
    
    async def get_all_active(self, user_id: uuid.UUID):
        return await self.repo.get_all(user_id, only_active=True)
    
    async def update(
            self,
            update_data: AccountUpdate,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ):
        updated = await self.repo.update(update_data, account_id, user_id)

        if not updated:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        return updated
    
    async def soft_delete(
            self,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ):
        await self.repo.soft_delete(account_id, user_id)

        return Response(status_code=status.HTTP_204_NO_CONTENT)