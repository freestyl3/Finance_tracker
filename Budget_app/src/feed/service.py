import uuid
import datetime as dt
from collections import defaultdict

from src.core.uow import IUnitOfWork
from src.feed.repository import FeedRepository
from src.feed.schemas import FeedResponse, FeedChain, FeedOperation
from src.operations.repository import OperationRepository
from src.feed.models import FeedItemORM
from src.common.utils import get_month_boundaries

class FeedService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    @property
    def feed_repo(self) -> FeedRepository:
        return self.uow.get_repo(FeedRepository)
    
    @property
    def op_repo(self) -> OperationRepository:
        return self.uow.get_repo(OperationRepository)

    async def get_feed(
            self,
            user_id: uuid.UUID,
            date_from: dt.date | None,
            date_to: dt.date | None,
            account_ids: list[uuid.UUID] | None = None,
            category_ids: list[uuid.UUID] | None = None,
            category_inside_chains: bool =  False
    ):
        today = dt.date.today()

        if date_from is None and date_to is None:
            date_from, date_to = get_month_boundaries(today.year, today.month)
        else:
            date_from = date_from or dt.date(2000, 1, 1)
            date_to = date_to or today

        items = await self.feed_repo.get_monthly_feed(
            start_date=date_from,
            end_date=date_to,
            user_id=user_id
        )

        max_past_date = await self.feed_repo.get_max_date_before(
            user_id=user_id,
            before_date=date_from
        )
        
        chain_ids = [i.id for i in items if i.entry_type == "chain"]

        operations = await self.op_repo.get_chains_operations(
            chain_ids=chain_ids,
            user_id=user_id
        )

        ops_dict = defaultdict(list)
        for op in operations:
            ops_dict[op.chain_id].append(op)
        
        prepared_items = []

        for item in items:
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

        if max_past_date:
            next_start, next_end = get_month_boundaries(
                max_past_date.year, 
                max_past_date.month
            )
            has_more = True
        else:
            next_start, next_end = None, None
            has_more = False
        
        return FeedResponse(
            items=prepared_items,
            next_start=next_start,
            next_end=next_end,
            has_more=has_more
        )
