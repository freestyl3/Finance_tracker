import uuid

from fastapi import APIRouter, Response, HTTPException

from src.categories.base.schemas import (
    CategoryCreate, CategoryRead, CategoryUpdate
)
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

@router.post("/batch_create", response_model=list[CategoryRead])
async def batch_create_categories(
    service: UserCategoryServiceDep,
    categories: GroupedAvailableCategories,
    user_id: CurrentUserID
):
    return await service.batch_create(categories, user_id)

@router.post("/", response_model=CategoryRead)
async def create_user_category(
    category: CategoryCreate,
    service: UserCategoryServiceDep,
    user_id: CurrentUserID
):
    try:
        return await service.create(category, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[CategoryRead])
async def get_all_user_categories(
    service: UserCategoryServiceDep,
    user_id: CurrentUserID
):
    return await service.get_all(user_id)

@router.put("/{category_id}", response_model=CategoryRead)
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
    result = await service.soft_delete(category_id, user_id)

    if result:
        return Response(status_code=204)
    raise HTTPException(status_code=404, detail="User category not found")