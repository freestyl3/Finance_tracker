from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}

@app.get("/index")
def index():
    return {"message": "Главная страница"}

@app.get("/users/{username}")
def get_user(username: str):
    return {"message": f"Профиль пользователя {username}"}

@app.post("/expenses")
def add_expense(expense: dict):
    return {"status": "ok", "data": expense}

items = {
    1: "Телефон",
    2: "Ноутбук",
    3: "Наушники",
    4: "Планшет"
}

@app.get("/search")
def search_item(name: str):
    results = [item for item in items.values() if name.lower() in item.lower()]
    return {"results": results}

@app.get("/items")
def get_items():
    return {"items": items}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id in items:
        return {
            "status": "ok",
            "item_id": item_id,
            "item": items[item_id]
        }
    return {"error": "Элемент не найден"}

@app.put("/items/{item_id}")
def update_item(item_id: int, name: str):
    if item_id in items:
        items[item_id] = name
        return {
            "status": "ok", 
            "item_id": item_id, 
            "item": items[item_id]
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Элемент не найден"
    )

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id in items:
        deleted = items.pop(item_id)
        return {"status": "ok", "item": deleted}
    return {"error": "Элемент не найден"}