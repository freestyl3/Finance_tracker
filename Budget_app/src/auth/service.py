import uuid

from src.auth.repository import UserRepository
from src.auth.models import User
from src.auth.security import verify_password, get_password_hash
from src.auth.schemas import UserCreate
from src.categories.user_categories.repository import UserCategoryRepository
from src.common.enums import OperationType
from src.core.uow import IUnitOfWork

class AuthService:
    def __init__(self, uow: IUnitOfWork):
        self.uow  = uow

    @property
    def user_repo(self) -> UserRepository:
        return self.uow.get_repo(UserRepository)
    
    @property
    def cat_repo(self) -> UserCategoryRepository:
        return self.uow.get_repo(UserCategoryRepository)

    def _get_initial_categories_data(self, user_id: uuid.UUID) -> list[dict]:
        return[
            {
                "name": "Перевод между счетами",
                "is_active": True,
                "deletable": False,
                "type": OperationType.TRANSFER,
                "user_id": user_id
            },
            {
                "name": "__balance_correction__",
                "is_active": True,
                "deletable": False,
                "type": OperationType.EXPENSE,
                "user_id": user_id
            },
            {
                "name": "__balance_correction__",
                "is_active": True,
                "deletable": False,
                "type": OperationType.INCOME,
                "user_id": user_id
            }
        ]

    async def create_user(self, create_schema: UserCreate) -> User:
        create_data = create_schema.model_dump(exclude=["password"])
        create_data["hashed_password"] = get_password_hash(create_schema.password)
        create_data["is_admin"] = False
        create_data["is_staff"] = False

        user = await self.user_repo.create(create_data)
        initial_categories_data = self._get_initial_categories_data(user.id)
        await self.cat_repo.batch_create(initial_categories_data)

        return user

    async def authenticate_user(self, username: str, password: str) -> User | None:
        user = await self.user_repo.get_one_by(username=username)

        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user