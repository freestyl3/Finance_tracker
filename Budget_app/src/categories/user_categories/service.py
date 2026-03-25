import uuid

from sqlalchemy.exc import IntegrityError

from src.base.service import ActiveNamedService
from src.categories.user_categories.repository import UserCategoryRepository
from src.categories.base.schemas import (
    CategoryCreate, GroupedAvailableCategories, CategoryRead
)
from src.categories.user_categories.models import UserCategory
from src.categories.system_categories.models import SystemCategory
from src.common.enums import OperationType

class UserCategoryService(ActiveNamedService[UserCategoryRepository]):
    def __init__(self, repo: UserCategoryRepository):
        super().__init__(repo)

    async def create(
            self,
            category_create: CategoryCreate,
            user_id: uuid.UUID
    ) -> UserCategory | None:
        category = await self.repo.create(
            category_data=category_create,
            user_id=user_id
        )

        if not category:
            await self.repo.session.rollback()
            raise ValueError("You already have category with this name and type!")

        await self.repo.session.commit()

        return category

    async def get_available_categories(
            self,
            user_id: uuid.UUID
    ) -> GroupedAvailableCategories:
        available_categories: list[SystemCategory] = list(
            await self.repo.get_available_for_user(user_id)
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
        return await self.repo.get_one_by(
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

        result = list(
            await self.repo.batch_create(
                categories=categories_to_create,
                user_id=user_id
            )
        )

        await self.repo.session.commit()
        return result

    async def soft_delete(
            self,
            model_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool:
        return await self.repo.delete(model_id, user_id)
        