from fastapi import Depends, HTTPException, Request

def get_current_user(request: Request):
    username = request.headers.get("X-Username")
    if username is None:
        raise HTTPException(status_code=401, detail="Username is required")
    return username

def ensure_user_active(username: str = Depends(get_current_user)):
    if username == "banned_user":
        raise HTTPException(status_code=403, detail="User is banned!")
    return username
