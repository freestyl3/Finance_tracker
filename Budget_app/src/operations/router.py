import uuid

from fastapi import APIRouter, HTTPException, Depends, Response, Query
from fastapi_filter import FilterDepends

from src.operations.dependencies import OperationServiceDep, TransferServiceDep
from src.auth.dependencies import CurrentUser
from src.operations.schemas import (
    OperationRead, OperationCreate, OperationUpdate, TransferCreate,
    TransferResponse
)
from src.pagination import PaginationParams
from src.operations.filters import OperationFilter

router = APIRouter()

@router.post("/", response_model=OperationRead)
async def create_operation(
    operation: OperationCreate,
    service: OperationServiceDep,
    current_user: CurrentUser
):
    try:
        return await service.create(operation, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/", response_model=list[OperationRead])
async def get_operations(
    service: OperationServiceDep,
    current_user: CurrentUser,
    filters: OperationFilter = FilterDepends(OperationFilter),
    pagination: PaginationParams = Depends()
):
    return await service.get_all(
        user_id=current_user.id,
        filters=filters,
        pagination=pagination
    )

@router.put("/{operation_id}", response_model=OperationRead)
async def update_operation(
    operation_id: uuid.UUID,
    service: OperationServiceDep,
    update_data: OperationUpdate,
    current_user: CurrentUser
):
    try:
        return await service.update(operation_id, update_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/{operation_id}")
async def delete_operation(
    operation_id: uuid.UUID,
    service: OperationServiceDep,
    current_user: CurrentUser
):
    try:
        await service.delete(operation_id, current_user.id)
        return Response(status_code=204)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.patch("/{operation_id}/ignore", response_model=OperationRead)
async def change_operation_visibility(
    operation_id: uuid.UUID,
    service: OperationServiceDep,
    current_user: CurrentUser
):
    return await service.change_visibility(operation_id, current_user.id)

@router.post("/transfer", response_model=TransferResponse)
async def create_transfer(
    service: TransferServiceDep,
    transfer: TransferCreate,
    current_user: CurrentUser
):
    try:
        op_out, op_in = await service.create(
            create_data=transfer,
            user_id=current_user.id
        )
        
        return TransferResponse(
            withdrawal=op_out,
            deposit=op_in
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
## Дописать обновление и удаление переводов
