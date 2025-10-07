from fastapi import APIRouter, Depends

from .dependencies import ensure_user_active

router = APIRouter()

@router.get("/me")
def get_me(current_user: str = Depends(ensure_user_active)):
    return {"message": f"Hello, {current_user}"}
