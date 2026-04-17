from typing import override

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.exceptions import UserAlreadyExistsError
from src.core.repository.base import BaseRepository
from src.core.enums import RepoAction

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    @override
    def _map_integrity_error(self, repo_action: RepoAction) -> Exception:
        if repo_action == RepoAction.CREATE:
            return UserAlreadyExistsError()
        return super()._map_integrity_error(repo_action)
