import uuid

from fastapi import APIRouter, Response, HTTPException

from src.categories.base.schemas import (
    CategoryCreate, CategoryRead, CategoryUpdate
)
from src.categories.user_categories.dependecies import UserCategoryServiceDep
from src.auth.dependencies import CurrentUser
from src.categories.base.schemas import GroupedAvailableCategories

router = APIRouter()

@router.get("/available", response_model=GroupedAvailableCategories)
async def get_available_categories(
    service: UserCategoryServiceDep,
    current_user: CurrentUser
):
    return await service.get_available_categories(current_user.id)

@router.post("/batch_create")
async def batch_create_categories(
    service: UserCategoryServiceDep,
    categories: GroupedAvailableCategories,
    current_user: CurrentUser
):
    return await service.batch_create(categories, current_user.id)

@router.post("/", response_model=CategoryRead)
async def create_user_category(
    category: CategoryCreate,
    service: UserCategoryServiceDep,
    current_user: CurrentUser
):
    return await service.create(category, current_user.id)

@router.get("/", response_model=list[CategoryRead])
async def get_all_user_categories(
    service: UserCategoryServiceDep,
    current_user: CurrentUser
):
    return await service.get_all(current_user.id)

@router.put("/{category_id}", response_model=CategoryRead)
async def update_user_category(
    category_id: uuid.UUID,
    category_update: CategoryUpdate,
    service: UserCategoryServiceDep,
    current_user: CurrentUser
):
    return await service.update(category_id, category_update, current_user.id)

@router.delete("/{category_id}")
async def delete_user_category(
    category_id: uuid.UUID,
    service: UserCategoryServiceDep,
    current_user: CurrentUser
):
    result = await service.soft_delete(category_id, current_user.id)

    if result:
        return Response(status_code=204)
    raise HTTPException(status_code=404, detail="User category not found")