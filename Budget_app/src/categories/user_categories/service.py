import uuid

from src.core.uow import IUnitOfWork
from src.categories.user_categories.exceptions import UserCategoryAlreadyExistsError
from src.categories.user_categories.repository import UserCategoryRepository
from src.operations.repository import OperationRepository
from src.categories.base.schemas import (
    CategoryCreate, GroupedAvailableCategories, CategoryUpdate
)
from src.categories.user_categories.models import UserCategory
from src.categories.system_categories.models import SystemCategory
from src.common.enums import OperationType

class UserCategoryService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    @property
    def cat_repo(self) -> UserCategoryRepository:
        return self.uow.get_repo(UserCategoryRepository)
    
    @property
    def op_repo(self) -> OperationRepository:
        return self.uow.get_repo(OperationRepository)

    async def create(
            self,
            category_create: CategoryCreate,
            user_id: uuid.UUID
    ) -> UserCategory:
        create_data = category_create.model_dump()

        category = await self.cat_repo.create(
            create_data=create_data,
            user_id=user_id
        )

        if not category:
            raise UserCategoryAlreadyExistsError()

        return category
    
    async def update(
            self,
            category_id: uuid.UUID,
            category_update: CategoryUpdate,
            user_id: uuid.UUID
    ) -> UserCategory:
        update_data = category_update.model_dump(exclude_unset=True)

        return await self.cat_repo.update(
            model_id=category_id,
            update_data=update_data,
            user_id=user_id
        )

    async def get_all(
            self,
            user_id: uuid.UUID,
            system: bool = False
    ) -> list[UserCategory]:
        return await self.cat_repo.get_all_by(
            user_id=user_id,
            deletable=not(system)
        )

    async def get_available_categories(
            self,
            user_id: uuid.UUID
    ) -> GroupedAvailableCategories:
        available_categories: list[SystemCategory] = list(
            await self.cat_repo.get_available_for_user(user_id)
        )

        expense_categories = [
            cat.name for cat in available_categories
            if cat.type == OperationType.EXPENSE
        ]

        income_categories = [
            cat.name for cat in available_categories
            if cat.type == OperationType.INCOME
        ]

        return GroupedAvailableCategories(
            expense_categories=expense_categories,
            income_categories=income_categories
        )
    
    async def get_correcting_category(
            self,
            op_type: OperationType,
            user_id: uuid.UUID
    ) -> UserCategory:
        return await self.cat_repo.get_one_by(
            user_id=user_id,
            name="__balance_correction__",
            type=op_type
        )

    async def batch_create(
            self,
            categories: GroupedAvailableCategories,
            user_id: uuid.UUID
    ) -> list[UserCategory]:
        expense_categories = [
            CategoryCreate(name=category, type=OperationType.EXPENSE)
            for category in categories.expense_categories
        ]
        income_categories = [
            CategoryCreate(name=category, type=OperationType.INCOME)
            for category in categories.income_categories
        ]

        categories_to_create = expense_categories + income_categories

        if not categories_to_create:
            return []
        
        create_data =[cat.model_dump() for cat in categories_to_create]

        return list(
            await self.cat_repo.batch_create(
                create_data=create_data,
                user_id=user_id
            )
        )

    async def soft_delete(
            self,
            category_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> UserCategory:
        return await self.cat_repo.update(
            model_id=category_id,
            update_data={
                "is_active": False
            },
            user_id=user_id
        )
    
    async def delete(
            self,
            category_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool:
        operations_exists = await self.op_repo.exists_by(
            category_id=category_id
        )

        if not operations_exists:
            await self.cat_repo.delete(
                model_id=category_id,
                user_id=user_id
            )
        await self.soft_delete(
            category_id=category_id,
            user_id=user_id
        )

        return True
         