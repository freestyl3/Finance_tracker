from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base
from src.common.enums import OperationType

class BaseCategory(Base):
    __abstract__ = True

    type: Mapped[OperationType] = mapped_column()
