import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_helper import db_helper
from src.auth.repository import UserRepository
from src.auth.service import AuthService
from src.auth.models import User
from src.auth.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    refreshUrl="/auth/refresh"
)

def get_user_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> UserRepository:
    return UserRepository(session)

def get_auth_service(
        user_repo: UserRepository = Depends(get_user_repository)
):
    return AuthService(user_repo)

def get_user_id(
        token: str = Depends(oauth2_scheme)
) -> uuid.UUID:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    payload = decode_token(token)

    if not payload:
        raise credentials_exception
    
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    user_id_str: str | None = payload.get("sub")

    if not user_id_str:
        raise credentials_exception
    
    try:
        return uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception
    
async def validate_refresh_token(
        grant_type: Annotated[str, Form()],
        token: Annotated[str, Form()],
        user_repo: UserRepository = Depends(get_user_repository)
):
    if grant_type != "refresh_token":
        raise HTTPException(status_code=401, detail="Invalid grant_type")
    
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    user_id_str: str | None = payload.get("sub")

    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid token data")
    
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token data")
    
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token data")
    
    return user_id

async def get_current_user(
        user_id: uuid.UUID = Depends(get_user_id),
        user_repo: UserRepository = Depends(get_user_repository)
) -> User:    
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user
    
async def ensure_user_is_staff(user: User = Depends(get_current_user)):
    if user.is_staff:
        return user
    raise HTTPException(status_code=403, detail="You don`t have permission!")

CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserID = Annotated[uuid.UUID, Depends(get_user_id)]
