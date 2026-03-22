import uuid

from fastapi import APIRouter, HTTPException, Depends, Response, Query
from fastapi_filter import FilterDepends

from src.operations.dependencies import OperationServiceDep, TransferServiceDep
from src.auth.dependencies import CurrentUserID
from src.operations.schemas import (
    OperationRead, OperationCreate, OperationUpdate, TransferCreate,
    TransferResponse, TransferUpdate
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
    try:
        return await service.create(operation, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
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

@router.put("/{operation_id}", response_model=OperationRead)
async def update_operation(
    operation_id: uuid.UUID,
    service: OperationServiceDep,
    update_data: OperationUpdate,
    user_id: CurrentUserID
):
    try:
        return await service.update(operation_id, update_data, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/{operation_id}")
async def delete_operation(
    operation_id: uuid.UUID,
    service: OperationServiceDep,
    user_id: CurrentUserID
):
    try:
        await service.delete(operation_id, user_id)
        return Response(status_code=204)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.patch("/{operation_id}/ignore", response_model=OperationRead)
async def change_operation_visibility(
    operation_id: uuid.UUID,
    service: OperationServiceDep,
    user_id: CurrentUserID
):
    try:
        return await service.change_visibility(operation_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/transfers", response_model=TransferResponse)
async def create_transfer(
    service: TransferServiceDep,
    transfer: TransferCreate,
    user_id: CurrentUserID
):
    try:
        op_out, op_in = await service.create(
            create_data=transfer,
            user_id=user_id
        )
        
        return TransferResponse(
            withdrawal=op_out,
            deposit=op_in
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/transfers/{operation_id}", response_model=TransferResponse)
async def update_transfer(
    operation_id: uuid.UUID,
    transfer_update: TransferUpdate,
    service: TransferServiceDep,
    user_id: CurrentUserID
):
    try:
        op_1, op_2 = await service.update(
            operation_id=operation_id,
            update_data=transfer_update,
            user_id=user_id
        )

        return TransferResponse(
            withdrawal=op_1,
            deposit=op_2
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
