import uuid

from sqlalchemy.exc import IntegrityError

from src.operations.repository import OperationRepository
from src.operations.schemas import OperationCreate, OperationUpdate
from src.operations.models import Operation
from src.pagination import PaginationParams
from src.base.filters import OperationFilterBase
from src.accounts.repository import AccountRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.common.enums import OperationType


class OperationService:
    def __init__(
            self,
            repo: OperationRepository,
            user_category_repository: UserCategoryRepository,
            account_repository: AccountRepository
    ):
        self.repo = repo
        self.cat_repo = user_category_repository
        self.account_repo = account_repository
    
    async def _validate_category(
            self,
            category_id: uuid.UUID,
            user_id: uuid.UUID,
            op_type: OperationType | None = None
    ) -> None:
        category = await self.cat_repo.get_by_id(
            category_id,
            user_id,
            only_active=True
        )

        if not category:
            raise ValueError("Category not found")
        
        if op_type and category.type != op_type:
            raise ValueError("Invalid category type")
        
    async def _validate_account(
            self,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> None:
        if not await self.account_repo.get_by_id(
            model_id=account_id,
            user_id=user_id,
            only_active=True
        ):
            raise ValueError("Could not validate account")

    async def create(
            self,
            user_id: uuid.UUID,
            create_data: OperationCreate
    ) -> Operation:
        await self._validate_category(
            category_id=create_data.category_id,
            type=create_data.type,
            user_id=user_id
        )

        await self._validate_account(
            account_id=create_data.account_id,
            user_id=user_id
        )
        
        try:
            new_operation = await self.repo.create(
                operation_data=create_data,
                user_id=user_id
            )
        except IntegrityError as e:
            raise ValueError(str(e))

        return new_operation

    async def get_all(
            self,
            user_id: uuid.UUID,
            filters: OperationFilterBase, 
            pagination: PaginationParams
    ) -> list[Operation]:
        # Тут еще доделать проверку на Account, когда дойду до фильтров
        if filters.category_id:
            await self._validate_category(
                category_id=filters.category_id,
                user_id=user_id
            )

        return await self.repo.get_all(user_id, filters, pagination)
    
    async def update(
            self,
            operation_id: uuid.UUID,
            update_data: OperationUpdate,
            user_id: uuid.UUID
    ):
        if update_data.account_id:
            await self._validate_account(
                account_id=update_data.account_id
            )

        if update_data.category_id:
            await self._validate_category(
                category_id=update_data.category_id,
                user_id=user_id
            )

        try:
            updated_operation = await self.repo.update(
                operation_id,
                update_data,
                user_id,
            )
        except IntegrityError as e:
            raise ValueError(str(e))

        if not updated_operation:
            raise ValueError("Operation not found or you don't have permission")
        
        return updated_operation

    async def delete(self, operation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        is_deleted = await self.repo.delete(operation_id, user_id)

        if not is_deleted:
            raise ValueError("Operation not found or you don't have permission")

        return True
