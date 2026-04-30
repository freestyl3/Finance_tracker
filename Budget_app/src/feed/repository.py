import uuid
import datetime as dt

from sqlalchemy import select, func, desc, Select, or_, and_, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.feed.models import FeedItemORM
from src.operations.models import Operation

class FeedRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _filter_by_params(
        self,
        query: Select,
        account_ids: list[uuid.UUID] | None,
        category_ids: list[uuid.UUID] | None,
        category_inside_chains: bool = False
    ) -> Select:
        if account_ids:
            chain_has_account = (
                select(1)
                .where(
                    Operation.chain_id == FeedItemORM.id,
                    Operation.account_id.in_(account_ids)
                )
                .exists()
            )

            query = query.where(
                or_(
                    FeedItemORM.account_id.in_(account_ids),
                    and_(
                        FeedItemORM.entry_type == "chain",
                        chain_has_account
                    )
                )
            )

        if category_ids:
            if category_inside_chains:
                chain_has_category = (
                    select(1)
                    .where(
                        Operation.chain_id == FeedItemORM.id,
                        Operation.category_id.in_(category_ids)
                    )
                    .exists()
                )
                
                query = query.where(
                    or_(
                        FeedItemORM.category_id.in_(category_ids),
                        and_(
                            FeedItemORM.entry_type == "chain",
                            chain_has_category
                        )
                    )
                )
            else:
                query = query.where(FeedItemORM.category_id.in_(category_ids))

        return query

    async def get_monthly_feed(
        self,
        start_date: dt.date,
        end_date: dt.date,
        user_id: uuid.UUID,
        account_ids: list[uuid.UUID] | None = None,
        category_ids: list[uuid.UUID] | None = None,
        category_inside_chains: bool = False
    ) -> Sequence[FeedItemORM]:
        query = (
            select(FeedItemORM)
            .where(
                FeedItemORM.user_id == user_id,
                FeedItemORM.date.between(start_date, end_date),
            )
            .options(
                joinedload(FeedItemORM.account),
                joinedload(FeedItemORM.category),
            )
            .order_by(desc(FeedItemORM.date))
        )

        query = self._filter_by_params(
            query,
            account_ids,
            category_ids,
            category_inside_chains
        )

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
