import uuid

from fastapi import APIRouter, Response

from src.transfers.dependencies import TransferServiceDep
from src.auth.dependencies import CurrentUserID
from src.transfers.schemas import (
    TransferCreate, TransferResponse, TransferUpdate
)

router = APIRouter()

@router.post("/", response_model=TransferResponse)
async def create_transfer(
    service: TransferServiceDep,
    transfer: TransferCreate,
    user_id: CurrentUserID
):
    op_out, op_in = await service.create(
        create_data=transfer,
        user_id=user_id
    )
    
    return TransferResponse(
        withdrawal=op_out,
        deposit=op_in
    )
    
@router.patch("/{transfer_id}/", response_model=TransferResponse)
async def update_transfer(
    transfer_id: uuid.UUID,
    transfer_update: TransferUpdate,
    service: TransferServiceDep,
    user_id: CurrentUserID
):
    op_1, op_2 = await service.update(
        operation_id=transfer_id,
        update_data=transfer_update,
        user_id=user_id
    )

    return TransferResponse(
        withdrawal=op_1,
        deposit=op_2
    )
    
@router.delete("/{transfer_id}")
async def delete_transfer(
    transfer_id: uuid.UUID,
    service: TransferServiceDep,
    user_id: CurrentUserID
):
    await service.delete(
        operation_id=transfer_id,
        user_id=user_id
    )
    return Response(status_code=204)
