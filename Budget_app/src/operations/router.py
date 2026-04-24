import uuid

from fastapi import APIRouter, Depends, Response
from fastapi_filter import FilterDepends

from src.operations.dependencies import OperationServiceDep
from src.auth.dependencies import CurrentUserID
from src.operations.schemas import (
    OperationRead, OperationCreate, OperationUpdate, 
)
from src.pagination import PaginationParams
from src.operations.filters import OperationFilter

router = APIRouter()

@router.post("/", response_model=OperationRead)
async def create_operation(
    operation: OperationCreate,
    service: OperationServiceDep,
    user_id: CurrentUserID
):
    return await service.create(operation, user_id)
    
@router.get("/", response_model=list[OperationRead])
async def get_operations(
    service: OperationServiceDep,
    user_id: CurrentUserID,
    filters: OperationFilter = FilterDepends(OperationFilter),
    pagination: PaginationParams = Depends()
):
    return await service.get_all(
        user_id=user_id,
        filters=filters,
        pagination=pagination
    )

@router.patch("/{operation_id}", response_model=OperationRead)
async def update_operation(
    operation_id: uuid.UUID,
    service: OperationServiceDep,
    update_data: OperationUpdate,
    user_id: CurrentUserID
):
    return await service.update(operation_id, update_data, user_id)
    
@router.delete("/{operation_id}")
async def delete_operation(
    operation_id: uuid.UUID,
    service: OperationServiceDep,
    user_id: CurrentUserID
):
    await service.delete(operation_id, user_id)
    return Response(status_code=204)
