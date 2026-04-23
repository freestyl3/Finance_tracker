from typing import Dict, Type

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.core.uow import T, IUnitOfWork

class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

        self._session: AsyncSession | None = None
        self._repos: Dict[Type, object] = {}

    async def start(self):
        if self._session is not None:
            raise RuntimeError("UoW already started")
        
        self._session = self._session_factory()
        self._repos.clear()

    async def commit(self):
        self._ensure_session()
        try:
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

    async def flush(self):
        self._ensure_session()
        await self._session.flush()

    async def rollback(self):
        self._ensure_session()
        await self._session.rollback()

    async def close(self):
        if self._session:
            await self._session.close()

        self._session = None
        self._repos.clear()

    def get_repo(self, repo_type: Type[T]) -> T:
        self._ensure_session()
        
        if repo_type not in self._repos:
            self._repos[repo_type] = repo_type(session=self._session)

        return self._repos[repo_type]

    def _ensure_session(self):
        if self._session is None:
            raise RuntimeError("UoW is not started")
