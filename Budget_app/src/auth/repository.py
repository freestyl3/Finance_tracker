from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.auth.schemas import UserCreate, UserRead
from src.auth.models import User
from src.auth.security import get_password_hash

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_create: UserCreate) -> User | None:
        hashed_password = get_password_hash(user_create.password)

        new_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password
        )

        self.session.add(new_user)

        try:
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user
        except IntegrityError:
            await self.session.rollback()
            return None
        
    async def get_user_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()
