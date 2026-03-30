import uuid
import datetime as dt

from src.feed.repository import FeedRepository
from src.feed.schemas import FeedResponse

class FeedService:
    def __init__(self, repo: type[FeedRepository]):
        self.repo = repo

    async def get_feed(
            self,
            year: int,
            month: int, 
            user_id: uuid.UUID
    ):
        result = await self.repo.get_monthly_feed(
            year=year,
            month=month,
            user_id=user_id
            # filters.account_ids,
            # filters.category_ids
        )
        
        first_day_of_current = dt.date(year, month, 1)
        next_hint = await self.repo.get_next_active_month(user_id, first_day_of_current)
        
        return FeedResponse(
            items=result,
            next_month=next_hint["month"] if next_hint else None,
            next_year=next_hint["year"] if next_hint else None,
            has_more=next_hint is not None,
            limit=0,
            offset=0
        )
