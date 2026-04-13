import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.auth.models import User
from src.auth.exceptions import UserAlreadyExistsError

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, create_data: dict) -> User:
        user = User(**create_data)
        self.session.add(user)
        
        try:
            await self.session.flush()
            return user
        except IntegrityError:
            raise UserAlreadyExistsError()        
        
    async def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()
    
    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.session.get(User, user_id)
