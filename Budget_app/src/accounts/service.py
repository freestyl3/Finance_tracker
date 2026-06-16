import uuid
from decimal import Decimal

from src.accounts.repository import AccountRepository
from src.accounts.schemas import AccountCreate, AccountUpdate
from src.accounts.models import Account
from src.categories.user_categories.repository import UserCategoryRepository
from src.operations.repository import OperationRepository
from src.common.enums import OperationType
from src.core.uow import IUnitOfWork
from src.accounts.exceptions import AccountNotFoundError
from src.accounts.schemas import AccountCheckResponse

class AccountService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    @property
    def acc_repo(self) -> AccountRepository:
        return self.uow.get_repo(AccountRepository)
    
    @property
    def cat_repo(self) -> UserCategoryRepository:
        return self.uow.get_repo(UserCategoryRepository)
    
    @property
    def op_repo(self) -> OperationRepository:
        return self.uow.get_repo(OperationRepository)

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
        data_dict = create_data.model_dump(exclude_unset=True)

        account = await self.acc_repo.create(
            create_data=data_dict,
            user_id=user_id
        )

        if not create_data.balance:
            return account
        
        await self.uow.flush()

        category = await self._get_correction_category(
            create_data.balance,
            user_id=user_id
        )
        
        await self.op_repo.create(
            {
                "amount": create_data.balance,
                "description": "Начальная корректировка счета",
                "account_id": account.id,
                "category_id": category.id
            },
            user_id=user_id
        )

        return account
    
    async def check_account_status(
            self,
            create_data: AccountCreate,
            user_id: uuid.UUID
    ) -> AccountCheckResponse:
        accounts: list[Account] = await self.acc_repo.get_all_by(
            user_id=user_id,
            **create_data.model_dump(exclude=["balance", ])
        )

        if not accounts:
            return AccountCheckResponse(status="free")
        
        active_account = next((acc for acc in accounts if acc.is_active), None)
        if active_account:
            return AccountCheckResponse(
                status="active_exists",
                active_account=active_account
            )
        
        return AccountCheckResponse(
            status="archived_exists",
            archived_accounts=accounts
        )
        
    async def restore(
            self,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Account:
        return await self.acc_repo.update(
            model_id=account_id,
            update_data={
                'is_active': True
            },
            user_id=user_id
        )

    async def get_all(
            self,
            user_id: uuid.UUID,
            is_active: bool = True
    ) -> list[Account]:
        return list(
            await self.acc_repo.get_all_by(
                user_id=user_id,
                is_active=is_active
            )
        )

    async def update(
            self,
            account_id: uuid.UUID,
            update_data: AccountUpdate,
            user_id: uuid.UUID
    ) -> Account:
        update_dict = update_data.model_dump(exclude_unset=True)

        if not update_dict:
            account = await self.acc_repo.get_one_by(
                id=account_id,
                user_id=user_id
            )

            if not account:
                raise AccountNotFoundError()

            return account

        if update_data.balance is not None:
            account = await self.acc_repo.get_one_by(
                id=account_id,
                user_id=user_id
            )

            delta = update_data.balance - account.balance

            if delta != 0:
                category = await self._get_correction_category(delta, user_id)

                await self.op_repo.create(
                    {
                        "amount": delta,
                        "description": "Корректировка счета",
                        "account_id": account.id,
                        "category_id": category.id
                    },
                    user_id=user_id
                )

        return await self.acc_repo.update(
            model_id=account_id,
            update_data=update_dict,
            user_id=user_id
        )
    
    async def soft_delete(
            self,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Account:
        return await self.acc_repo.update(
            model_id=account_id,
            update_data={
                "is_active": False
            },
            user_id=user_id
        )
    
    async def delete(
            self,
            account_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool:
        operations_exists = await self.op_repo.exists_by(
            user_id=user_id,
            account_id=account_id
        )

        if not operations_exists:
            await self.acc_repo.delete(
                model_id=account_id,
                user_id=user_id
            )
            return True
        
        await self.soft_delete(
            account_id=account_id,
            user_id=user_id
        )
        return True
