from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession

class RepositoryProtocol(Protocol):
    def __init__(self, session: AsyncSession): ...
