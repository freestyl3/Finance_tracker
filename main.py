from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}

@app.get('/index')
def index():
    return {"message": "Главная страница"}

@app.get('/users/{username}')
def get_user(username: str):
    return {"message": f"Профиль пользователя {username}"}

@app.get('/items/{item_id}')
def get_item(item_id: int):
    return {"item_id": item_id, "status": "ok"}
