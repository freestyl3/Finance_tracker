from typing import Literal

from pydantic import BaseModel

from src.categories.base.schemas import CategoryRead

class UserCategoryRead(CategoryRead):
    is_active: bool

class DeleteUserCategoryResponse(BaseModel):
    status: Literal["archived", "deleted"]
