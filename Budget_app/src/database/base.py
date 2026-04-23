import uuid
import uuid6

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.types import Uuid


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid6.uuid7
    )
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"