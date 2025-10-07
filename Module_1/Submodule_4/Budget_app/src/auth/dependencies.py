from fastapi import Query, HTTPException

def get_current_user(username: str | None = Query(None)):
    if username is None:
        raise HTTPException(status_code=400, detail="Username is required")
    return username