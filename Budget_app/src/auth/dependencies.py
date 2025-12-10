from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_helper import db_helper
from src.auth.repository import UserRepository
from src.auth.service import AuthService

def get_current_user(request: Request):
    username = request.headers.get("X-Username")
    if username is None:
        raise HTTPException(status_code=401, detail="Username is required")
    return username

def ensure_user_active(username: str = Depends(get_current_user)):
    if username == "banned_user":
        raise HTTPException(status_code=403, detail="User is banned!")
    return username

def get_user_repository(
        session: AsyncSession = Depends(db_helper.session_dependency)
) -> UserRepository:
    return UserRepository(session)

def get_auth_service(
        user_repo: UserRepository = Depends(get_user_repository)
):
    return AuthService(user_repo)
