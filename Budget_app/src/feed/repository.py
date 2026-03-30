import uuid
import datetime as dt

from sqlalchemy import select, func, union_all, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.operations.models import Operation
from src.chains.models import Chain
from src.feed.models import FeedItemORM

class FeedRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_monthly_feed(
        self,  
        year: int, 
        month: int,
        user_id: uuid.UUID,
        account_ids: list[uuid.UUID] | None = None,
        category_ids: list[uuid.UUID] | None = None
    ):
        start_date = dt.date(year, month, 1)
        if month == 12:
            end_date = dt.date(year, month, 31)
        else:
            end_date = dt.date(year, month + 1, 1) - dt.timedelta(days=1)

        query = select(FeedItemORM).where(
            FeedItemORM.user_id == user_id,
            FeedItemORM.date.between(start_date, end_date)
        )

        query = (
            query.options(
                joinedload(FeedItemORM.account),
                joinedload(FeedItemORM.category)
            )
            .order_by(desc(FeedItemORM.date))
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_next_active_month(self, user_id: uuid.UUID, before_date: dt.date):
        # subq = union_all(
        #     select(Operation.date).where(Operation.user_id == user_id, Operation.date < before_date),
        #     select(Chain.date).where(Chain.user_id == user_id, Chain.date < before_date)
        # ).subquery()
        subq = select(
            FeedItemORM.date
        ).where(
            FeedItemORM.user_id == user_id,
            FeedItemORM.date < before_date
        ).subquery()
        
        query = select(func.max(subq.c.date))
        max_date = await self.session.scalar(query)
        
        if max_date:
            return {"year": max_date.year, "month": max_date.month}
        return None