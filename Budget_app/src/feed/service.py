import uuid
from collections import defaultdict
from datetime import datetime

from src.core.uow import IUnitOfWork
from src.feed.repository import FeedRepository
from src.feed.schemas import FeedResponse, FeedChain, FeedOperation, FeedTransfer
from src.operations.repository import OperationRepository
from src.feed.models import FeedItemORM
from src.feed.schemas import FeedItem
from src.feed.filters import FeedFilter
from src.operations.models import Operation
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
    
    def _validate_for_response(
        self, 
        feed_items: list[FeedItemORM],
        chain_operations: list[Operation],
        transfer_operations: dict[uuid.UUID, Operation]
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
            elif item.entry_type == "transfer":
                prepared_items.append(
                    FeedTransfer.model_validate({
                        **item.__dict__,
                        "account_from": transfer_operations[item.related_operation_id].account,
                        "account_to": item.account
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
        if not(filters.date_from and filters.date_to):
            today_date = datetime.today()
            filters.date_from, filters.date_to = get_month_boundaries(
                today_date.year,
                today_date.month
            )

        items: list[FeedItemORM] = await self.feed_repo.get_monthly_feed(
            user_id=user_id,
            filters=filters
        )

        date_from, date_to = None, None

        if len(items) > filters.limit:
            last_item = items[-1]
            filters.offset += 1
            next_date = last_item.date
            items = items[:-1]
        else:
            filters.offset = None
            max_date = filters.date_from
            if items:
                max_date = items[-1].date
            next_date = await self.feed_repo.get_max_date_before(user_id, max_date)
        
        if next_date:
            date_from, date_to = get_month_boundaries(
                next_date.year,
                next_date.month
            )

        chain_ids = [i.id for i in items if i.entry_type == "chain"]
        target_transfer_ids = [
            i.related_operation_id for i in items if i.entry_type == "transfer"
        ]

        operations = await self.op_repo.get_chains_operations(
            chain_ids=chain_ids,
            user_id=user_id
        )

        transfers = await self.op_repo.get_operations_for_chain(
            operation_ids=target_transfer_ids,
            user_id=user_id,
            chain_id=None,
            allow_free=True
        )

        transfers_dict = dict(zip(target_transfer_ids, transfers))
        
        prepared_items = self._validate_for_response(
            feed_items=items,
            chain_operations=operations,
            transfer_operations=transfers_dict
        )

        return FeedResponse(
            items=prepared_items,
            date_from=date_from,
            date_to=date_to,
            offset=filters.offset
        )
