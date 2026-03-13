import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.base.service import ActiveNamedService
from src.categories.user_categories.repository import UserCategoryRepository
from src.categories.base.schemas import (
    CategoryCreate, GroupedAvailableCategories, CategoryRead
)
from src.categories.user_categories.models import UserCategory
from src.common.enums import OperationType
from src.categories.system_categories.service import SystemCategoryService
from src.categories.system_categories.repository import SystemCategoryRepository

class UserCategoryService(ActiveNamedService[UserCategoryRepository]):
    def __init__(self, repo: UserCategoryRepository):
        super().__init__(repo)

    async def create(
            self,
            category_create: CategoryCreate,
            user_id: uuid.UUID
    ) -> UserCategory | None:
        try:
            new_category = await self.repo.create(
                category_data=category_create,
                user_id=user_id
            )
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have category with this name and type!"
            )
        
        return new_category

    async def get_available_categories(
            self,
            user_id: uuid.UUID
    ) -> GroupedAvailableCategories:
        sys_repo = SystemCategoryRepository(self.repo.session)
        sys_service = SystemCategoryService(sys_repo)

        available_categories = await sys_service.get_available_for_user(user_id)

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
        results = []
        for cat in categories.expense_categories:
            try:
                category = await self.create(
                    CategoryCreate(name=cat, type=OperationType.EXPENSE),
                    user_id
                )
                results.append(
                    CategoryRead(
                        id=category.id,
                        name=category.name,
                        type=category.type
                    )
                )
            except IntegrityError:
                continue
        for cat in categories.income_categories:
            try:
                category = await self.create(
                    CategoryCreate(name=cat, type=OperationType.INCOME),
                    user_id
                )
                results.append(
                    CategoryRead(
                        id=category.id,
                        name=category.name,
                        type=category.type
                    )
                )
            except IntegrityError:
                continue

        return results

    async def soft_delete(
            self,
            model_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool:
        return await self.repo.delete(model_id, user_id)
        