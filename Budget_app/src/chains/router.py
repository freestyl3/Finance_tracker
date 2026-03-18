from fastapi import APIRouter, HTTPException

from src.auth.dependencies import CurrentUser
from src.chains.schemas import (
    ChainPreview, ChainPreviewResponse, ChainCreate, ChainRead
)
from src.chains.dependencies import ChainServiceDep

router = APIRouter()

@router.post("/preview", response_model=ChainPreviewResponse)
async def preview_chain(
    chain_preview: ChainPreview,
    service: ChainServiceDep,
    current_user: CurrentUser
):
    return await service.preview_chain(chain_preview, current_user.id)

@router.post("/", response_model=ChainRead)
async def create_chain(
    chain_create: ChainCreate,
    service: ChainServiceDep,
    current_user: CurrentUser
):
    try:
        return await service.create(chain_create, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
