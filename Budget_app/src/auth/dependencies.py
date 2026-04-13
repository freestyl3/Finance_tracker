import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer

from src.auth.repository import UserRepository
from src.database.repositories import get_user_repository
# from src.categories.user_categories.repository import UserCategoryRepository
# from src.database.repositories import get_user_category_repository
from src.auth.service import AuthService
from src.auth.models import User
from src.auth.security import decode_token
from src.core.uow import IUnitOfWork
from src.infrasturcture.dependencies import get_uow

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    refreshUrl="/auth/refresh"
)

async def get_auth_service(
        uow: IUnitOfWork = Depends(get_uow)
) -> AuthService:
    return AuthService(uow)

# async def get_auth_service(
#         user_repository: UserRepository = Depends(get_user_repository),
#         user_category_repository: UserCategoryRepository = Depends(get_user_category_repository)
# ):
#     return AuthService(
#         user_repository=user_repository,
#         user_category_repository=user_category_repository
#     )

async def get_user_id(
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
        uow: IUnitOfWork = Depends(get_uow)
) -> User:
    user_repo = uow.get_repo(UserRepository)
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
