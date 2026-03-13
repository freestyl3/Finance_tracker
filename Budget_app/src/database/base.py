from datetime import datetime
import uuid
import uuid6

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy import String, func, ForeignKey, UniqueConstraint
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
    

## Вроде уже не надо    

# class CategoryBase(Base):
#     __abstract__ = True

#     name: Mapped[str] = mapped_column(String(127), index=True)
#     user_id: Mapped[int] = mapped_column(
#         ForeignKey("users.id", ondelete="CASCADE")
#     )

#     @declared_attr
#     def __table_args__(cls):
#         return (
#             UniqueConstraint(
#                 "name", "user_id", name=f"uq_{cls.__tablename__}_name_user"
#             ),
#         )
    

# class AbstractOperation(Base):
#     __abstract__ = True
    
#     amount: Mapped[float] = mapped_column()
#     description: Mapped[str|None] = mapped_column(String(255), nullable=True)
#     date: Mapped[datetime] = mapped_column(default=datetime.today)
#     created_at: Mapped[datetime] = mapped_column(server_default=func.now())
#     category_id: Mapped[int] = mapped_column()
#     category: Mapped[CategoryBase] = mapped_column() # Добавить BaseOperationCategory

#     user_id: Mapped[int] = mapped_column(
#         ForeignKey("users.id", ondelete="CASCADE")
#     )

class CategoryBase:
    pass

class AbstractOperation:
    pass
