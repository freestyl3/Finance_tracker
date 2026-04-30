import datetime as dt

from fastapi import APIRouter, Query

from src.feed.schemas import FeedResponse
from src.feed.dependencies import FeedServiceDep
from src.auth.dependencies import CurrentUserID

router = APIRouter()

@router.get("/", response_model=FeedResponse)
async def get_feed(
    service: FeedServiceDep,
    user_id: CurrentUserID,
    date_from: dt.date | None = Query(None),
    date_to: dt.date | None = Query(None)
):
    return await service.get_feed(
        user_id=user_id,
        date_from=date_from,
        date_to=date_to
    )
