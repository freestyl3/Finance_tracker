import uuid
import datetime as dt

from sqlalchemy import select, func, desc, Select, or_, and_, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.feed.models import FeedItemORM
from src.operations.models import Operation
from src.categories.user_categories.models import UserCategory
from src.feed.filters import FeedFilter

class FeedRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _filter_by_params(self, query: Select, filters: FeedFilter) -> Select:
        if filters.type:
            query = query.join(
                UserCategory, FeedItemORM.category_id == UserCategory.id
            ).where(
                UserCategory.type == filters.type
            )

        if filters.account_ids:
            chain_has_account = (
                select(1)
                .where(
                    Operation.chain_id == FeedItemORM.id,
                    Operation.account_id.in_(filters.account_ids)
                )
                .exists()
            )

            query = query.where(
                or_(
                    FeedItemORM.account_id.in_(filters.account_ids),
                    and_(
                        FeedItemORM.entry_type == "chain",
                        chain_has_account
                    )
                )
            )

        if filters.category_ids:
            if filters.category_inside_chains:
                chain_has_category = (
                    select(1)
                    .where(
                        Operation.chain_id == FeedItemORM.id,
                        Operation.category_id.in_(filters.category_ids)
                    )
                    .exists()
                )
                
                query = query.where(
                    or_(
                        FeedItemORM.category_id.in_(filters.category_ids),
                        and_(
                            FeedItemORM.entry_type == "chain",
                            chain_has_category
                        )
                    )
                )
            else:
                query = query.where(FeedItemORM.category_id.in_(filters.category_ids))

        if filters.search_query:
            query = query.where(
                FeedItemORM.description.ilike(f"%{filters.search_query}%")
            )

        if filters.cursor_date and filters.cursor_id:
            query = query.where(
                or_(
                    FeedItemORM.date < filters.cursor_date,
                    and_(
                        FeedItemORM.date == filters.cursor_date,
                        FeedItemORM.id < filters.cursor_id
                    )
                )
            )

        return query

    async def get_monthly_feed(
        self,
        user_id: uuid.UUID,
        filters: FeedFilter
    ) -> Sequence[FeedItemORM]:
        query = (
            select(FeedItemORM)
            .where(
                FeedItemORM.user_id == user_id,
                FeedItemORM.date.between(filters.date_from, filters.date_to),
            )
            .options(
                joinedload(FeedItemORM.account),
                joinedload(FeedItemORM.category),
            )
            .order_by(desc(FeedItemORM.date))
        )

        query = self._filter_by_params(query, filters)
        
        query = query.order_by(
            desc(FeedItemORM.date),
            desc(FeedItemORM.id)
        )
        
        query = query.limit(filters.limit + 1)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_max_date_before(
        self,
        user_id: uuid.UUID, 
        before_date: dt.date
    ) -> dt.date | None:
        query = select(
            func.max(FeedItemORM.date)
        ).where(
            FeedItemORM.user_id == user_id,
            FeedItemORM.date < before_date
        )
        
        return await self.session.scalar(query)
