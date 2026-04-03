import uuid
import datetime as dt
from collections import defaultdict

from src.feed.repository import FeedRepository
from src.feed.schemas import FeedResponse, FeedChain, FeedOperation
from src.operations.repositories.operation_chain_repository import OperationChainRepository
from src.feed.models import FeedItemORM

class FeedService:
    def __init__(
            self,
            repository: type[FeedRepository],
            operation_repository: type[OperationChainRepository]):
        self.repo = repository
        self.op_repo = operation_repository

    async def get_feed(
            self,
            year: int,
            month: int, 
            user_id: uuid.UUID
    ):
        items: list[FeedItemORM] = await self.repo.get_monthly_feed(
            year=year,
            month=month,
            user_id=user_id
            # filters.account_ids,
            # filters.category_ids
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

        first_day_of_current = dt.date(year, month, 1)
        next_hint = await self.repo.get_next_active_month(user_id, first_day_of_current)
        
        return FeedResponse(
            items=prepared_items,
            next_month=next_hint["month"] if next_hint else None,
            next_year=next_hint["year"] if next_hint else None,
            has_more=next_hint is not None,
            limit=0,
            offset=0
        )
