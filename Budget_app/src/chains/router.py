import uuid

from fastapi import APIRouter, HTTPException, Response

from src.auth.dependencies import CurrentUserID
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
    user_id: CurrentUserID
):
    try:
        return await service.create(chain_create, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[ChainShortRead])
async def get_all_chains(
    service: ChainServiceDep,
    user_id: CurrentUserID
):
    return await service.get_all(user_id)

@router.get("/{chain_id}", response_model=ChainDetailRead)
async def get_chain(
    chain_id: uuid.UUID,
    service: ChainServiceDep,
    user_id: CurrentUserID
):
    try:
        return await service.get_by_id(chain_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/{chain_id}/operations/add")
async def add_operations_to_chain(
    chain_id: uuid.UUID,
    update_schema: ChainOperationsUpdate,
    service: ChainServiceDep,
    user_id: CurrentUserID
):
    try:
        return await service.add_operations_into_chain(
            chain_id,
            update_schema,
            user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/{chain_id}/operations/remove")
async def remove_operations_from_chain(
    chain_id: uuid.UUID,
    update_schema: ChainOperationsUpdate,
    service: ChainServiceDep,
    user_id: CurrentUserID
):
    try:
        return await service.remove_operations_from_chain(
            chain_id,
            update_schema,
            user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{chain_id}")
async def delete_chain(
    chain_id: uuid.UUID,
    service: ChainServiceDep,
    user_id: CurrentUserID
):
    try:
        await service.delete(chain_id, user_id)
        return Response(status_code=204)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
