from typing import override

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository.base import BaseRepository
from src.categories.system_categories.models import SystemCategory
from src.core.enums import RepoAction
from src.categories.system_categories.exceptions import (
    SystemCategoryAlreadyExistsError, SystemCategoryNotFoundError
)

class SystemCategoryRepository(BaseRepository[SystemCategory]):
    def __init__(self, session: AsyncSession):
        super().__init__(SystemCategory, session)

    @override
    def _map_integrity_error(self, repo_action: RepoAction) -> Exception:
        if repo_action == RepoAction.CREATE:
            return SystemCategoryAlreadyExistsError()
        return super()._map_integrity_error(repo_action)

    @override
    def _not_found(self) -> Exception:
        return SystemCategoryNotFoundError()
