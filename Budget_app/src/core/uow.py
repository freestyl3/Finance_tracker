from abc import ABC, abstractmethod
from typing import Type, TypeVar
from src.core.repository import RepositoryProtocol

T = TypeVar("T", bound=RepositoryProtocol)

class IUnitOfWork(ABC):
    @abstractmethod
    def get_repo(self, repo_type: Type[T]) -> T:
        """
        Возвращает репозиторий, привязанный к текущей транзакции.
        """
        ...

    @abstractmethod
    async def flush(self) -> None:
        """
        Принудительно отправляет изменения в БД без commit.
        Нужен, например, чтобы получить ID.
        """
        ...

    @abstractmethod
    async def commit(self) -> None:
        """
        Явный commit (используется редко, для специальных сценариев).
        """
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """
        Явный rollback (обычно не нужен, но оставляем для гибкости).
        """
        ...
