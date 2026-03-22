from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.dependencies import (
    get_user_repository, get_auth_service, CurrentUser, validate_refresh_token
)
from src.auth.schemas import UserCreate, UserRead, TokenResponse
from src.auth.repository import UserRepository
from src.auth.security import create_access_token, create_refresh_token
from src.auth.service import AuthService
from src.auth.models import User

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: CurrentUser
):
    return current_user

@router.post("/register", response_model=UserRead)
async def register_user(
    user_create: UserCreate,
    repo: UserRepository = Depends(get_user_repository)
):
    user = await repo.create(user_create)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered."
        )
    
    return user

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    user = await service.authenticate_user(
        form_data.username,
        form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW_Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    token = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

    return token

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    user_id: str = Depends(validate_refresh_token) 
):
    access_token = create_access_token(data={"sub": str(user_id)})
    refresh_token = create_refresh_token(data={"sub": str(user_id)})

    token = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

    return token
