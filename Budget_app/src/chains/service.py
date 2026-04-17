import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.attributes import set_committed_value

from src.chains.repository import ChainRepository
from src.operations.repository import OperationRepository
from src.chains.schemas import (
    ChainMetadata, ChainCreate, ChainOperationsUpdate, ChainUpdate
)
from src.chains.models import Chain
from src.common.enums import OperationType
from src.categories.user_categories.repository import UserCategoryRepository
from src.operations.models import Operation

class ChainService:
    def __init__(
            self,
            chain_repository: ChainRepository,
            operation_repository: OperationRepository,
            category_repository: UserCategoryRepository
    ):
        self.repo = chain_repository
        self.op_repo = operation_repository
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

        operations_count = len(operations)

        if operations_count < 2:
            raise ValueError("Can't create chain with less than 2 operations")

        if operations_count != len(operation_ids):
            raise ValueError("Some operations not found, not yours or already in other chain")

        total_amount = sum(operation.amount for operation in operations)

        unique_types = {operation.category.type for operation in operations}

        if OperationType.TRANSFER in unique_types:
            raise ValueError("Transfer can't be in chain")
        
        return ChainMetadata(
            total_amount=total_amount,
            operations=operations,
            operations_count=operations_count,
            suggested_type=self._suggest_type(total_amount)
        )
    
    async def _validate_and_get_category_id(
        self,
        prev_category_id: uuid.UUID | None,
        new_category_id: uuid.UUID | None,
        prev_amount: Decimal,
        delta: Decimal,
        user_id: uuid.UUID
    ) -> uuid.UUID | None:
        prev_type = self._suggest_type(prev_amount)
        
        new_amount = prev_amount + delta
        new_type = self._suggest_type(new_amount)

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
            delta: Decimal
    ) -> Chain:
        if chain.category_id != new_category_id:
            chain.category_id = new_category_id
        
        chain.operations_count = len(operations)
        chain.amount += delta

        await self.repo.session.commit()

        set_committed_value(chain, 'operations', operations)

        return chain

    async def create(
            self,
            create_data: ChainCreate,
            user_id: uuid.UUID
    ) -> Chain:
        if len(create_data.operation_ids) < 2:
            raise ValueError("Can't create chain with less than 2 operations")

        meta = await self._validate_and_get_metadata(
            operation_ids=create_data.operation_ids,
            user_id=user_id,
            chain_id=None,
            allow_free=True
        )
        
        data_dict = create_data = create_data.model_dump(exclude=["operation_ids",])

        if meta.suggested_type:
            if not create_data.category_id:
                raise ValueError("Category is required for this chain sum")
            
            category = await self.cat_repo.get_by_id(
                create_data.category_id, user_id
            )
            if not category or category.type != meta.suggested_type:
                raise ValueError(f"Required category type: {meta.suggested_type}")
        else:
            data_dict["category_id"] = None
            # create_data.category_id = None

        data_dict["amount"] = meta.total_amount
        data_dict["operations_count"] = meta.operations_count

        try:
            chain = await self.repo.create(data_dict, user_id)

            await self._update_operations(
                create_data.operation_ids,
                chain.id,
                user_id
            )

            await self.repo.session.commit()

            set_committed_value(chain, 'operations', list(meta.operations))

            return chain
        
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))
    
    async def get_all(self, user_id: uuid.UUID) -> list[Chain]:
        return list(
            await self.repo.get_all(
                user_id,
                joinedload(Chain.category)
            )
        )
    
    async def get_by_id(
            self,
            chain_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Chain:
        chain = await self.repo.get_by_id(
            chain_id,
            user_id,
            joinedload(Chain.category),
            selectinload(Chain.operations).joinedload(Operation.category),
            selectinload(Chain.operations).joinedload(Operation.account)
        )

        if not chain:
            raise ValueError("Chain not found")

        return chain
    
    async def update(
            self,
            chain_id: uuid.UUID,
            update_schema: ChainUpdate,
            user_id: uuid.UUID
    ) -> Chain:
        chain = await self.get_by_id(chain_id, user_id)

        if not chain:
            raise ValueError("Chain not found")
        
        update_data = update_schema.model_dump(exclude_unset=True)

        if not update_data:
            return chain
        
        category = chain.category

        if "category_id" in update_data:
            new_cat_id = update_data["category_id"]
            expected_type = self._suggest_type(chain.amount)

            if new_cat_id is None:
                if expected_type is not None:
                    raise ValueError(
                        f"Required category type: {expected_type}"
                    )
            else:
                if new_cat_id != chain.category_id:
                    category = await self.cat_repo.get_by_id(new_cat_id, user_id)
                    if not category:
                        raise ValueError("Category not found")
                    
                    if category.type != expected_type:
                        raise ValueError(f"Required category type: {expected_type}")
        try:
            updated = await self.repo.update(chain_id, update_data, user_id)

            await self.repo.session.commit()

            set_committed_value(updated, 'category', category)
            set_committed_value(updated, 'operations', chain.operations)
            
            return updated
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))
    
    async def delete(
            self,
            chain_id: uuid.UUID,
            cascade: bool,
            user_id: uuid.UUID
    ) -> bool:
        try:
            deleted = await self.repo.delete(chain_id, user_id)

            if not deleted:
                raise ValueError("Chain not found")
            
            # if cascade:
            #     await self.op_repo.delete_chain_operations(chain_id, user_id)
            #     await self.acc_repo.update_balance(
            #         account_id=deleted.account_id,
            #         delta=-deleted.amount,
            #         user_id=user_id
            #     )

            await self.repo.session.commit()
            return True
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))
    
    async def add_operations_into_chain(
            self,
            chain_id: uuid.UUID,
            update_schema: ChainOperationsUpdate,
            user_id: uuid.UUID
    ) -> Chain:
        chain = await self.get_by_id(chain_id, user_id)

        requested_operations = await self.op_repo.get_operations_for_chain(
            operation_ids=update_schema.operation_ids,
            user_id=user_id,
            chain_id=chain_id,
            allow_free=True
        )

        if len(requested_operations) != len(set(update_schema.operation_ids)):
            raise ValueError("Some operations were not found or don't belong to you")
        
        unique_types = {operation.category.type for operation in requested_operations}

        if OperationType.TRANSFER in unique_types:
            raise ValueError("Transfer can't be in chain")

        to_add = [
            operation for operation in requested_operations
            if operation.chain_id is None
        ]

        prev_amount = chain.amount
        delta = sum(operation.amount for operation in to_add)

        new_category_id = await self._validate_and_get_category_id(
            chain.category_id,
            update_schema.category_id,
            prev_amount,
            delta,
            user_id
        )

        if not to_add and chain.category_id == new_category_id:
            return chain

        try:
            new_operations = []

            if to_add:
                new_operations = await self._update_operations(
                    [operation.id for operation in to_add],
                    chain_id,
                    user_id
                )

            operations = chain.operations + new_operations

            return await self._finalize_chain_update(
                chain,
                new_category_id,
                operations,
                delta
            )
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))
        
    async def remove_operations_from_chain(
            self,
            chain_id: uuid.UUID,
            update_schema: ChainOperationsUpdate,
            user_id: uuid.UUID
    ) -> Chain | None:
        chain = await self.get_by_id(chain_id, user_id)
        
        to_remove = [
            op for op in chain.operations
            if op.id in update_schema.operation_ids
        ]

        prev_amount = chain.amount
        delta = -sum(operation.amount for operation in to_remove)

        new_category_id = await self._validate_and_get_category_id(
            chain.category_id,
            update_schema.category_id,
            prev_amount,
            delta,
            user_id
        )

        if not to_remove and chain.category_id == new_category_id:
            return chain
        
        to_stay = [
            op for op in chain.operations
            if op.id not in update_schema.operation_ids
        ]

        if len(to_stay) < 2:
            await self.delete(chain_id, user_id)
            return None

        try:
            if to_remove:
                await self._update_operations(
                    [operation.id for operation in to_remove],
                    None,
                    user_id
                )

            return await self._finalize_chain_update(
                chain,
                new_category_id,
                to_stay,
                delta
            )
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))
