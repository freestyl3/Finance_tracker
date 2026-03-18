import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from src.chains.repository import ChainRepository
from src.operations.repository import OperationRepository
from src.chains.schemas import ChainPreview, ChainPreviewResponse, ChainCreate
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

    async def preview_chain(
            self,
            chain_preview: ChainPreview,
            user_id: uuid.UUID
    ) -> ChainPreviewResponse:
        operation_uuids = chain_preview.operation_uuids
        rows = await self.op_repo.get_info_for_chain_validation(
            operation_uuids,
            user_id
        )

        unique_accounts = set(r.account_id for r in rows)
        unique_types = set(r.type for r in rows)

        found_count = rows[0].found_count if rows else 0

        can_create = True
        error_message = None

        if found_count != len(operation_uuids):
            can_create = False
            error_message = "Некоторые операции не найдены, вам не принадлежат или УЖЕ находятся в другой цепочке"

        elif len(unique_accounts) > 1:
            can_create = False
            error_message = "Нельзя объединять операции с разных счетов"

        elif OperationType.TRANSFER in unique_types:
            can_create = False
            error_message = "В цепочке не должно быть переводов"

        total_amount = Decimal("0.0")
        if can_create:
            total_amount = await self.op_repo.get_sum_of_operations(
                operation_uuids,
                user_id
            )
            account = await self.acc_repo.get_by_id(
                tuple(unique_accounts)[0],
                user_id
            )
        
        if can_create:
            return ChainPreviewResponse(
                can_create=can_create,
                operations_count=len(operation_uuids),
                operations_sum=total_amount,
                allowed_category_type=self._suggest_type(total_amount),
                account=account,
                operation_uuids=operation_uuids,
                error_message=None
            )
        return ChainPreviewResponse(
            can_create=can_create,
            operations_count=None,
            operations_sum=None,
            allowed_category_type=None,
            account=None,
            operation_uuids=None,
            error_message=error_message
        )

    async def create(
            self,
            create_data: ChainCreate,
            user_id: uuid.UUID
    ) -> Chain:
        preview = await self.preview_chain(create_data, user_id)

        if not preview.can_create:
            raise ValueError(f"Can't create chain - {preview.error_message}")
        
        if preview.allowed_category_type:
            if not create_data.category_id:
                raise ValueError("Category is required for this chain sum")
            
            category = await self.cat_repo.get_by_id(
                create_data.category_id, user_id
            )
            if not category or category.type != preview.allowed_category_type:
                raise ValueError(f"Required category type: {preview.allowed_category_type}")
        else:
            create_data.category_id = None
        
        amount = preview.operations_sum
        account_id = preview.account.id

        try:
            new_chain = await self.repo.create(
                create_data,
                amount,
                account_id,
                user_id
            )

            await self._update_operations(
                create_data.operation_uuids,
                new_chain.id
            )

            await self.repo.session.commit()
            await self.repo.session.refresh(new_chain)

            return new_chain
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))

