import uuid

from fastapi import APIRouter, Depends, Response

from src.categories.base.schemas import CategoryRead, CategoryCreate
from src.categories.system_categories.schemas import SystemCategoryUpdate
from src.categories.system_categories.dependecies import SystemCategoryServiceDep
from src.auth.dependencies import ensure_user_is_staff

router = APIRouter(dependencies=[Depends(ensure_user_is_staff)])

@router.post("/", response_model=CategoryRead)
async def create_system_category(
    category: CategoryCreate,
    service: SystemCategoryServiceDep
):
    return await service.create(category)

@router.get("/", response_model=list[CategoryRead])
async def get_all_system_categories(service: SystemCategoryServiceDep):
    return await service.get_all()

@router.patch("/{category_id}", response_model=CategoryRead)
async def update_system_category(
    category_id: uuid.UUID,
    category_update: SystemCategoryUpdate,
    service: SystemCategoryServiceDep
):
    return await service.update(category_id, category_update)

@router.delete("/{category_id}")
async def delete_system_category(
    category_id: uuid.UUID,
    service: SystemCategoryServiceDep
):
    await service.delete(category_id)
    return Response(status_code=204)
