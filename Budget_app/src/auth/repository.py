import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.auth.schemas import UserCreate
from src.auth.models import User
from src.auth.security import get_password_hash
from src.categories.user_categories.models import UserCategory
from src.common.enums import OperationType

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_create: UserCreate) -> User | None:
        hashed_password = get_password_hash(user_create.password)

        new_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            is_admin=False,
            is_staff=False
        )

        self.session.add(new_user)

        try:
            await self.session.flush()
            self._create_default_categories(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user
        except IntegrityError:
            await self.session.rollback()
            return None
        
    def _create_transfer_category(self, user: User) -> None:
        category = UserCategory(
            name="Перевод между счетами",
            is_active=False,
            deletable=False,
            type=OperationType.TRANSFER,
            user_id=user.id
        )

        self.session.add(category)

    def _create_correct_balance_categories(self, user: User) -> None:
        name = "__balance_correction__"

        category_expense = UserCategory(
            name=name,
            is_active=False,
            deletable=False,
            type=OperationType.EXPENSE,
            user_id=user.id
        )

        category_income = UserCategory(
            name=name,
            is_active=False,
            deletable=False,
            type=OperationType.INCOME,
            user_id=user.id
        )

        self.session.add_all([category_expense, category_income])
        
    def _create_default_categories(self, user: User) -> None:
        self._create_transfer_category(user)
        self._create_correct_balance_categories(user)
        
    async def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()
    
    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.session.get(User, user_id)
