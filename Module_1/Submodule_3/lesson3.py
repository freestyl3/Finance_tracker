from fastapi import FastAPI
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    age: int

app = FastAPI()

@app.post("/users")
def create_user(user: User):
    return {"message": f"User {user.name} created!", "user": user}

