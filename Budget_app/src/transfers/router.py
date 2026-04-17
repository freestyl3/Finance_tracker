import uuid

from fastapi import APIRouter, HTTPException

from src.transfers.dependencies import TransferServiceDep
from src.auth.dependencies import CurrentUserID
from src.transfers.schemas import (
    TransferCreate, TransferResponse, TransferUpdate
)

router = APIRouter()

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
    
@router.patch("/transfers/{operation_id}", response_model=TransferResponse)
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
    
# ДОБАВИТЬ DELETE МЕТОД
