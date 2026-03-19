import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import set_committed_value

from src.chains.repository import ChainRepository
from src.operations.repository import OperationRepository
from src.chains.schemas import (
    ChainMetadata, ChainCreate, ChainDetailRead, ChainShortRead
)
from src.chains.models import Chain
from src.common.enums import OperationType
from src.accounts.repository import AccountRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.operations.models import Operation

class ChainService:
    def __init__(
            self,
            chain_repository: ChainRepository,
            operation_repository: OperationRepository,
            account_repository: AccountRepository,
            category_repository: UserCategoryRepository
    ):
        self.repo = chain_repository
        self.op_repo = operation_repository
        self.acc_repo = account_repository
        self.cat_repo = category_repository

    def _suggest_type(self, amount: Decimal) -> OperationType | None:
        if amount > 0: return OperationType.INCOME
        if amount < 0: return OperationType.EXPENSE
        return None
    
    async def _update_operations(
            self,
            operation_uuids: list[uuid.UUID],
            chain_id: uuid.UUID
    ) -> Operation:
        return await self.op_repo.update_with_chain(operation_uuids, chain_id)

    async def _validate_and_get_metadata(
            self,
            operation_ids: list[uuid.UUID],
            user_id: uuid.UUID
    ) -> ChainMetadata:
        operations = await self.op_repo.get_operations_for_chain(
            operation_ids,
            user_id
        )

        if len(operations) != len(operation_ids):
            raise ValueError("Some operations not found, not yours or already in other chain")

        unique_accounts = {operation.account for operation in operations}
        total_amount = sum(operation.amount for operation in operations)

        if len(unique_accounts) > 1:
            raise ValueError("Can't union operations from different accounts")

        unique_types = {operation.category.type for operation in operations}

        if OperationType.TRANSFER in unique_types:
            raise ValueError("Transfer can't be in chain")
        
        return ChainMetadata(
            total_amount=total_amount,
            account=operations[0].account,
            operations=operations,
            suggested_type=self._suggest_type(total_amount)
        )


    async def create(
            self,
            create_data: ChainCreate,
            user_id: uuid.UUID
    ) -> ChainDetailRead:
        meta = await self._validate_and_get_metadata(
            create_data.operation_uuids,
            user_id
        )
        
        if meta.suggested_type:
            if not create_data.category_id:
                raise ValueError("Category is required for this chain sum")
            
            category = await self.cat_repo.get_by_id(
                create_data.category_id, user_id
            )
            if not category or category.type != meta.suggested_type:
                raise ValueError(f"Required category type: {meta.suggested_type}")
        else:
            create_data.category_id = None

        try:
            new_chain = await self.repo.create(
                create_data,
                meta.account.id,
                user_id
            )

            await self._update_operations(
                create_data.operation_uuids,
                new_chain.id
            )

            await self.repo.session.commit()
            await self.repo.session.refresh(new_chain)

            set_committed_value(new_chain, 'operations', list(meta.operations))

            return ChainDetailRead(
                **new_chain.__dict__,
                amount=meta.total_amount,
                operations_count=len(meta.operations)
            )
        
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))
    
    async def get_all(self, user_id: uuid.UUID) -> list[ChainShortRead]:
        return await self.repo.get_all(user_id)
