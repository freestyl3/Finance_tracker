from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, func

from src.database.base import Base

if TYPE_CHECKING:
    from src.expenses.models import Expense
    from src.incomes.models import Income

class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    incomes: Mapped[list["Income"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
