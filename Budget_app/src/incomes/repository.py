from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.incomes.models import Income
from src.incomes.schemas import IncomeCreate, IncomeUpdate

class IncomeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_income(self, income_data: IncomeCreate, user_id: int) -> Income:
        income = Income(**income_data.model_dump(), user_id=user_id)
        self.session.add(income)
        await self.session.commit()
        await self.session.refresh(income)
        return income
    
    async def get_incomes(self, user_id: int) -> list[Income]:
        query = select(Income).where(Income.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_income_by_id(self, income_id: int, user_id: int) -> Income | None:
        query = select(Income).where(
            Income.id == income_id,
            Income.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()
    
    async def delete_income(self, income_id: int, user_id: int) -> bool:
        query = delete(Income).where(
            Income.id == income_id,
            Income.user_id == user_id
        )
        result = await self.session.execute(query)
        await self.session.commit()

        return result.rowcount > 0
    
    async def update_income(
            self,
            income_id: int,
            user_id: int,
            income_update: IncomeUpdate
    ) -> Income:
        income = await self.get_income_by_id(income_id, user_id)
        if not income:
            return None

        update_data = income_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(income, key, value)

        await self.session.commit()
        await self.session.refresh(income)

        return income
