import uuid

from fastapi import APIRouter, Response

from src.categories.base.schemas import CategoryCreate, CategoryUpdate
from src.categories.user_categories.schemas import UserCategoryRead
from src.categories.user_categories.dependecies import UserCategoryServiceDep
from src.auth.dependencies import CurrentUserID
from src.categories.base.schemas import GroupedAvailableCategories

router = APIRouter()

@router.get("/available", response_model=GroupedAvailableCategories)
async def get_available_categories(
    service: UserCategoryServiceDep,
    user_id: CurrentUserID
):
    return await service.get_available_categories(user_id)

@router.post("/batch_create", response_model=list[UserCategoryRead])
async def batch_create_categories(
    service: UserCategoryServiceDep,
    categories: GroupedAvailableCategories,
    user_id: CurrentUserID
):
    return await service.batch_create(categories, user_id)

@router.post("/", response_model=UserCategoryRead)
async def create_user_category(
    category: CategoryCreate,
    service: UserCategoryServiceDep,
    user_id: CurrentUserID
):
    return await service.create(category, user_id)

@router.get("/", response_model=list[UserCategoryRead])
async def get_all_user_categories(
    service: UserCategoryServiceDep,
    user_id: CurrentUserID
):
    return await service.get_all(user_id)

@router.patch("/{category_id}", response_model=UserCategoryRead)
async def update_user_category(
    category_id: uuid.UUID,
    category_update: CategoryUpdate,
    service: UserCategoryServiceDep,
    user_id: CurrentUserID
):
    return await service.update(category_id, category_update, user_id)

@router.delete("/{category_id}")
async def delete_user_category(
    category_id: uuid.UUID,
    service: UserCategoryServiceDep,
    user_id: CurrentUserID
):
    await service.delete(category_id, user_id)
    return Response(status_code=204)
