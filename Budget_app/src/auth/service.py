from src.auth.repository import UserRepository
from src.auth.models import User
from src.auth.security import verify_password

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate_user(self, username: str, password: str) -> User | None:
        user = await self.user_repo.get_by_username(username)

        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user