from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy import String, func

class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    

class OperationBase(Base):
    __abstract__ = True
    
    amount: Mapped[float] = mapped_column()
    description: Mapped[str|None] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(127), index=True)
    date: Mapped[datetime] = mapped_column(default=datetime.today)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
