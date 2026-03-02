from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, func

from src.database.base import Base
from src.accounts.models import Account

# if TYPE_CHECKING:
#     from src.expenses.models import Expense
#     from src.incomes.models import Income

class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_admin: Mapped[bool] = mapped_column(
        server_default="FALSE",
        nullable=False
    )
    is_staff: Mapped[bool] = mapped_column(
        server_default="FALSE",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    accounts: Mapped[list["Account"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # expenses: Mapped[list["Expense"]] = relationship(
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )
    # incomes: Mapped[list["Income"]] = relationship(
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )
