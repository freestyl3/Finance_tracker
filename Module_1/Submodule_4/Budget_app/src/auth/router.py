from fastapi import APIRouter, Depends

from .dependencies import get_current_user

router = APIRouter()

@router.get("/me")
def get_me(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello, {current_user}"}
