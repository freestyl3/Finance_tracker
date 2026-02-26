from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base
### Temporary import
from src.operations.models import OperationType

class BaseCategory(Base):
    __abstract__ = True

    type: Mapped[OperationType] = mapped_column()