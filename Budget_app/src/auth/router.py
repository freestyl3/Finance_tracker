from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.dependencies import get_user_repository, get_auth_service, get_current_user
from src.auth.schemas import UserCreate, UserRead, Token
from src.auth.repository import UserRepository
from src.auth.security import create_access_token
from src.auth.service import AuthService
from src.auth.models import User

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

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

@router.post("/login", response_model=Token)
async def login_for_access_token(
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

    token = Token(
        access_token=access_token,
        token_type="bearer"
    )

    return token
