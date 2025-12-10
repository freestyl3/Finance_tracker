from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import get_user_repository
from src.auth.schemas import UserCreate, UserRead
from src.auth.repository import UserRepository

router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register_user(
    user_create: UserCreate,
    repo: UserRepository = Depends(get_user_repository)
):
    user = await repo.create_user(user_create)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered."
        )
    
    return user
