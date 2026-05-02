from fastapi import APIRouter
from fastapi_filter import FilterDepends

from src.feed.schemas import FeedResponse
from src.feed.dependencies import FeedServiceDep
from src.auth.dependencies import CurrentUserID
from src.feed.filters import FeedFilter

router = APIRouter()

@router.get("/", response_model=FeedResponse)
async def get_feed(
    service: FeedServiceDep,
    user_id: CurrentUserID,
    filters: FeedFilter = FilterDepends(FeedFilter)
):
    return await service.get_feed(
        user_id=user_id,
        filters=filters
    )
