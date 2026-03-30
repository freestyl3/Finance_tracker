from fastapi import APIRouter, Query

from src.feed.schemas import FeedResponse
from src.feed.dependencies import FeedServiceDep
from src.auth.dependencies import CurrentUserID

router = APIRouter()

@router.get("/", response_model=FeedResponse)
async def get_feed(
    service: FeedServiceDep,
    user_id: CurrentUserID,
    year: int = Query(...),
    month: int = Query(...)
):
    return await service.get_feed(year, month, user_id)
