import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import set_committed_value

from src.chains.repository import ChainRepository
from src.operations.repository import OperationRepository
from src.chains.schemas import (
    ChainMetadata, ChainCreate, ChainDetailRead, ChainOperationsUpdate
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
            chain_id: uuid.UUID | None,
            user_id: uuid.UUID
    ) -> list[Operation]:
        if operation_uuids:
            return await self.op_repo.update_with_chain(
                operation_uuids,
                chain_id,
                user_id
            )
        return []

    async def _validate_and_get_metadata(
            self,
            operation_ids: list[uuid.UUID],
            user_id: uuid.UUID,
            chain_id: uuid.UUID | None = None,
            allow_free: bool = False
    ) -> ChainMetadata:       
        operations = await self.op_repo.get_operations_for_chain(
            operation_ids=operation_ids,
            user_id=user_id,
            chain_id=chain_id,
            allow_free=allow_free
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

    # async def _validate_and_get_category_id(
    #         self,
    #         prev_category_id: uuid.UUID | None,
    #         new_category_id: uuid.UUID | None,
    #         prev_type: OperationType,
    #         new_type: OperationType,
    #         user_id: uuid.UUID
    # ) -> uuid.UUID | None:
    #     if new_type is None:
    #         return None
        
    #     if new_type != prev_type:
    #         if not new_category_id:
    #             raise ValueError(f"Need category_id with type - {new_type}")
            
    #         category = await self.cat_repo.get_by_id(
    #             new_category_id,
    #             user_id
    #         )

    #         if not category:
    #             raise ValueError("Category not found")
            
    #         if category.type != new_type:
    #             raise ValueError(f"Need category_id with type - {new_type}")
            
    #         return new_category_id
            
    #     if new_category_id:
    #         category = await self.cat_repo.get_by_id(
    #             new_category_id,
    #             user_id
    #         )

    #         if not category:
    #             raise ValueError("Category not found")
            
    #         if category.type != new_type:
    #             raise ValueError(f"Need category_id with type - {new_type}")
            
    #         return new_category_id
    #     return prev_category_id
    
    async def _validate_and_get_category_id(
        self,
        prev_category_id: uuid.UUID | None,
        new_category_id: uuid.UUID | None,
        prev_type: OperationType | None,
        new_type: OperationType | None,
        user_id: uuid.UUID
    ) -> uuid.UUID | None:
        if new_type is None:
            return None

        if new_category_id:
            category = await self.cat_repo.get_by_id(new_category_id, user_id)
            if not category or category.type != new_type:
                raise ValueError(f"Category not found or invalid type. Expected: {new_type}")
            return new_category_id

        if prev_type != new_type:
            raise ValueError(f"Current category mismatch new sum sign. Need category with type: {new_type}")

        return prev_category_id
    
    async def _finalize_chain_update(
            self,
            chain: Chain,
            new_category_id: uuid.UUID | None,
            operations: list[Operation],
            new_amount: Decimal
    ) -> ChainDetailRead:
        if chain.category_id != new_category_id:
            chain.category_id = new_category_id
        
        chain.operations_count = len(operations)
        chain.amount = new_amount

        await self.repo.session.commit()
        await self.repo.session.refresh(chain)

        set_committed_value(chain, 'operations', operations)

        return ChainDetailRead.model_validate(chain)

    async def create(
            self,
            create_data: ChainCreate,
            user_id: uuid.UUID
    ) -> ChainDetailRead:
        if len(create_data.operation_uuids) < 2:
            raise ValueError("Can't create chain with less than 2 operations")

        meta = await self._validate_and_get_metadata(
            operation_ids=create_data.operation_uuids,
            user_id=user_id,
            chain_id=None,
            allow_free=True
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
                new_chain.id,
                user_id
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
    
    async def get_all(self, user_id: uuid.UUID) -> list[Chain]:
        return await self.repo.get_all(user_id)
    
    async def get_by_id(
            self,
            chain_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Chain:
        chain = await self.repo.get_by_id(chain_id, user_id)

        if not chain:
            raise ValueError("Chain not found")

        return chain
    
    async def delete(
            self,
            chain_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool:
        deleted = await self.repo.delete(chain_id, user_id)

        if not deleted:
            raise ValueError("Chain not found")
        return deleted
    
    async def add_operations_into_chain(
            self,
            chain_id: uuid.UUID,
            update_schema: ChainOperationsUpdate,
            user_id: uuid.UUID
    ) -> ChainDetailRead:
        chain = await self.get_by_id(chain_id, user_id)

        all_operations = await self.op_repo.get_all_for_chain_update(
            user_id,
            chain_id,
            update_schema.operation_ids
        )

        prev_operations = [
            operation for operation in all_operations
            if operation.chain_id == chain_id
        ]

        input_ids = set(update_schema.operation_ids)
        requested_operations = [
            operation for operation in all_operations
            if operation.id in input_ids
        ]

        if len(requested_operations) != len(input_ids):
            raise ValueError("Some operations were not found or don't belong to you")
        
        for operation in requested_operations:
            if (
                operation.chain_id is not None
                and operation.chain_id != chain_id
            ):
                raise ValueError(f"Operation {operation.id} already belongs to another chain")

        to_add = [
            operation for operation in requested_operations
            if operation.chain_id is None
        ]

        prev_amount = sum(operation.amount for operation in prev_operations)
        prev_type = self._suggest_type(prev_amount)

        amount_to_add = sum(operation.amount for operation in to_add)
        
        new_amount = prev_amount + amount_to_add
        new_type = self._suggest_type(new_amount)

        new_category_id = await self._validate_and_get_category_id(
            chain.category_id,
            update_schema.category_id,
            prev_type,
            new_type,
            user_id
        )

        if not to_add and chain.category_id == new_category_id:
            return ChainDetailRead.model_validate(chain)

        try:
            if to_add:
                new_operations = await self._update_operations(
                    [operation.id for operation in to_add],
                    chain_id,
                    user_id
                )

            operations = list(
                set.union(set(prev_operations), set(new_operations))
            )

            return await self._finalize_chain_update(
                chain,
                new_category_id,
                operations,
                new_amount
            )
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))
        
    async def remove_operations_from_chain(
            self,
            chain_id: uuid.UUID,
            update_schema: ChainOperationsUpdate,
            user_id: uuid.UUID
    ) -> ChainDetailRead | None:
        chain = await self.get_by_id(chain_id, user_id)

        all_operations = chain.operations
        
        to_remove = [
            op for op in all_operations 
            if op.id in update_schema.operation_ids
        ]

        if not to_remove:
            return ChainDetailRead.model_validate(chain)
        
        to_stay = [
            op for op in all_operations
            if op.id not in update_schema.operation_ids
        ]

        if not to_remove:
            raise ValueError("No operations for remove")

        if len(to_stay) < 2:
            await self.delete(chain_id, user_id)
            return None
        
        prev_amount = sum(operation.amount for operation in all_operations)
        sum_to_remove = sum(operation.amount for operation in to_remove)

        new_amount = prev_amount - sum_to_remove

        prev_type = self._suggest_type(prev_amount)
        new_type = self._suggest_type(new_amount)

        new_category_id = await self._validate_and_get_category_id(
            chain.category_id,
            update_schema.category_id,
            prev_type,
            new_type,
            user_id
        )

        try:
            await self._update_operations(
                [operation.id for operation in to_remove],
                None,
                user_id
            )

            return await self._finalize_chain_update(
                chain,
                new_category_id,
                to_stay,
                new_amount
            )
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))
