import uuid

from fastapi import APIRouter, HTTPException, Response

from src.auth.dependencies import CurrentUser
from src.chains.schemas import (
    ChainCreate, ChainDetailRead, ChainShortRead, ChainOperationsUpdate
)
from src.chains.dependencies import ChainServiceDep
from src.pagination import PaginationParams

router = APIRouter()

@router.post("/", response_model=ChainDetailRead)
async def create_chain(
    chain_create: ChainCreate,
    service: ChainServiceDep,
    current_user: CurrentUser
):
    try:
        return await service.create(chain_create, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[ChainShortRead])
async def get_all_chains(
    service: ChainServiceDep,
    current_user: CurrentUser
):
    return await service.get_all(current_user.id)

@router.get("/{chain_id}", response_model=ChainDetailRead)
async def get_chain(
    chain_id: uuid.UUID,
    service: ChainServiceDep,
    current_user: CurrentUser
):
    try:
        return await service.get_by_id(chain_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/{chain_id}/operations/add")
async def add_operations_to_chain(
    chain_id: uuid.UUID,
    update_schema: ChainOperationsUpdate,
    service: ChainServiceDep,
    current_user: CurrentUser
):
    try:
        return await service.add_operations_into_chain(
            chain_id,
            update_schema,
            current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{chain_id}")
async def delete_chain(
    chain_id: uuid.UUID,
    service: ChainServiceDep,
    current_user: CurrentUser
):
    try:
        await service.delete(chain_id, current_user.id)
        return Response(status_code=204)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
