import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_helper import db_helper
from src.auth.repository import UserRepository
from src.auth.service import AuthService
from src.auth.models import User
from src.auth.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_user_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> UserRepository:
    return UserRepository(session)

def get_auth_service(
        user_repo: UserRepository = Depends(get_user_repository)
):
    return AuthService(user_repo)

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    payload = decode_access_token(token)

    if not payload:
        raise credentials_exception
    
    user_id_str: str | None = payload.get("sub")

    if not user_id_str:
        raise credentials_exception
    
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception
    
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise credentials_exception
    
    return user
    
async def ensure_user_is_staff(user: User = Depends(get_current_user)):
    if user.is_staff:
        return user
    raise HTTPException(status_code=403, detail="You don`t have permission!")

CurrentUser = Annotated[User, Depends(get_current_user)]
