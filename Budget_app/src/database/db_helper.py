from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.core.config import settings

class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )

    async def dispose(self):
        await self.engine.dispose()

    "Нужно будет удалить позже после переписывания репозиториев"
    async def session_dependency(self):
        async with self.session_factory() as session:
            yield session

db_helper = DatabaseHelper(
    settings.db.url,
    echo=True
)
