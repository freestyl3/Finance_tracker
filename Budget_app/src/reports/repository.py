import uuid
import datetime as dt

from sqlalchemy import Sequence, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.reports.filters import ReportFilter
from src.categories.user_categories.models import UserCategory
from src.feed.models import FeedItemORM
from src.common.enums import OperationType

class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_report(
        self,
        filters: ReportFilter,
        user_id: uuid.UUID
    ) -> Sequence[tuple[UserCategory, float]]:
        query = select(
            UserCategory,
            func.sum(FeedItemORM.amount).label("amount")
        ).join(
            FeedItemORM, UserCategory.id == FeedItemORM.category_id
        ).where(
            UserCategory.type != OperationType.TRANSFER,
            FeedItemORM.user_id == user_id,
            FeedItemORM.date.between(
                filters.date_from,
                filters.date_to
            ),
            FeedItemORM.ignore.is_(False)
        ).group_by(
            UserCategory.id
        )

        result = await self.session.execute(query)
        return result.all()
