import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from src.base.service import ActiveNamedService
from src.accounts.repository import AccountRepository
from src.accounts.schemas import AccountCreate
from src.accounts.models import Account
from src.categories.user_categories.repository import UserCategoryRepository
from src.operations.repositories.repository import OperationRepository
from src.common.enums import OperationType
from src.operations.schemas import OperationCreate

class AccountService(ActiveNamedService[AccountRepository]):
    def __init__(
            self,
            account_repository: AccountRepository,
            user_category_repository: UserCategoryRepository,
            operation_repository: OperationRepository
    ):
        super().__init__(account_repository)
        self.cat_repo = user_category_repository
        self.op_repo = operation_repository

    async def _get_correction_category(
            self,
            amount: Decimal,
            user_id: uuid.UUID
    ):
        if amount > 0:
            return await self.cat_repo.get_one_by(
                user_id=user_id,
                name="__balance_correction__",
                type=OperationType.INCOME
            )
        return await self.cat_repo.get_one_by(
                user_id=user_id,
                name="__balance_correction__",
                type=OperationType.EXPENSE
            )

    async def create(
            self,
            create_data: AccountCreate,
            user_id: uuid.UUID
    ) -> Account:
        try:
            account = await self.repo.create(
                account_data=create_data,
                user_id=user_id
            )


            if create_data.balance:
                await self.repo.session.flush()

                category = await self._get_correction_category(
                    create_data.balance,
                    user_id=user_id
                )

                await self.op_repo.create(
                    OperationCreate.model_construct(
                        amount=create_data.balance,
                        description="Начальная корректировка счета",
                        account_id=account.id,
                        category_id=category.id
                    ),
                    user_id=user_id
                )

            await self.repo.session.commit()
            await self.repo.session.refresh(account)

            return account
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise ValueError(str(e))
    
    async def check_deleted(
            self,
            create_data: AccountCreate,
            user_id: uuid.UUID
    ) -> uuid.UUID:
        existing = await self.repo.get_one_by(
            user_id=user_id,
            **create_data.model_dump(exclude=["balance", ]),
            is_active=False
        )

        if existing:
            return existing.id
        return None
        
    async def restore(
            self,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Account:
        account = await self.repo.restore(
            account_id=account_id,
            user_id=user_id
        )

        await self.repo.session.commit()
        return account