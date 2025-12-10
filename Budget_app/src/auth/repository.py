from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.auth.schemas import UserCreate, UserRead
from src.auth.models import User
from src.auth.security import get_password_hash
from src.expenses.models import ExpenseCategory
from src.incomes.models import IncomeCategory

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
            await self.session.flush()
            await self._create_default_categories(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user
        except IntegrityError:
            await self.session.rollback()
            return None
        
    async def _create_default_categories(self, user: User) -> None:
        default_expenses = ["Еда", "Транспорт", "Жилье", "Развлечения", "Здоровье"]
        for name in default_expenses:
            expense = ExpenseCategory(name=name, user_id=user.id)
            self.session.add(expense)

        default_incomes = ["Зарплата", "Фриланс", "Подарки", "Инвестиции"]
        for name in default_incomes:
            income = IncomeCategory(name=name, user_id=user.id)
            self.session.add(income)
        
    async def get_user_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)
