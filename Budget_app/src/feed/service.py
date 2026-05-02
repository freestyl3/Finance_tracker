import uuid
import datetime as dt
from collections import defaultdict

from src.core.uow import IUnitOfWork
from src.feed.repository import FeedRepository
from src.feed.schemas import FeedResponse, FeedChain, FeedOperation
from src.operations.repository import OperationRepository
from src.feed.models import FeedItemORM
from src.feed.schemas import FeedItem
from src.common.utils import get_month_boundaries
from src.feed.filters import FeedFilter
from src.operations.models import Operation

class FeedService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    @property
    def feed_repo(self) -> FeedRepository:
        return self.uow.get_repo(FeedRepository)
    
    @property
    def op_repo(self) -> OperationRepository:
        return self.uow.get_repo(OperationRepository)
    
    def _validate_for_response(
        self, 
        feed_items: list[FeedItemORM],
        chain_operations: list[Operation]
    ) -> list[FeedItem]:
        ops_dict = defaultdict(list)
        for op in chain_operations:
            ops_dict[op.chain_id].append(op)
        
        prepared_items = []

        for item in feed_items:
            if item.entry_type == "chain":
                prepared_items.append(
                    FeedChain.model_validate({
                        **item.__dict__,
                        "operations": ops_dict.get(item.id, [])
                    })
                )
            else:
                prepared_items.append(
                    FeedOperation.model_validate(item)
                )

        return prepared_items

    async def get_feed(
            self,
            user_id: uuid.UUID,
            filters: FeedFilter
    ) -> FeedResponse:
        today = dt.date.today()

        if filters.date_from is None and filters.date_to is None:
            filters.date_from, filters.date_to = get_month_boundaries(today.year, today.month)
        else:
            filters.date_from = filters.date_from or dt.date(2000, 1, 1)
            filters.date_to = filters.date_to or today

        items = await self.feed_repo.get_monthly_feed(
            user_id=user_id,
            filters=filters
        )

        has_more = False
        if len(items) > filters.limit:
            has_more = True
            items = items[:-1]

        chain_ids = [i.id for i in items if i.entry_type == "chain"]

        operations = await self.op_repo.get_chains_operations(
            chain_ids=chain_ids,
            user_id=user_id
        )
        
        prepared_items = self._validate_for_response(
            feed_items=items,
            chain_operations=operations
        )

        next_cursor_date = None
        next_cursor_id = None
        next_start = None
        next_end = None

        if has_more and prepared_items:
            last_item = prepared_items[-1]
            next_cursor_date = last_item.date
            next_cursor_id = last_item.id
            next_start=filters.date_from
            next_end=filters.date_to
        else:
            max_past_date = await self.feed_repo.get_max_date_before(
                user_id=user_id,
                before_date=filters.date_from
            )

            if max_past_date:
                next_start, next_end = get_month_boundaries(max_past_date.year, max_past_date.month)
                has_more = True

        return FeedResponse(
            items=prepared_items,
            has_more=has_more,
            next_cursor_date=next_cursor_date,
            next_cursor_id=next_cursor_id,
            next_start=next_start,
            next_end=next_end
        )
