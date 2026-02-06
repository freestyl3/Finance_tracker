from decimal import Decimal
from enum import Enum
import datetime as dt
import uuid

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, ForeignKey, UniqueConstraint, Numeric, func

from database.base import Base

class AccountType(Enum):
    DEBIT = "debit"
    CASH = "cash"


class Currency(Enum):
    RUB = "rub"


class Account(Base):
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[AccountType] = mapped_column()
    currency: Mapped[Currency] = mapped_column()
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2),
        server_default="0"
    )
    is_active: Mapped[bool] = mapped_column(server_default="true")

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    __table_args__ = (
        UniqueConstraint(
            "name", "user_id", "is_active",
            name="uq_accounts_name_user_is_active"
        ),
    )


class OperationType(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class BaseCategory(Base):
    __abstract__ = True

    type: Mapped[OperationType] = mapped_column()


class SystemCategory(BaseCategory):
    __tablename__ = "sys_categories"

    name: Mapped[str] = mapped_column(String(255), unique=True)
    can_disable: Mapped[bool] = mapped_column(server_default="false")


class UserCategory(BaseCategory):
    __tablename__ = "user_categories"

    name: Mapped[str] = mapped_column(String(255))
    can_disable: Mapped[bool] = mapped_column(server_default="true")
    is_active: Mapped[bool] = mapped_column(server_default="true")

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    __table_args__ = (
        UniqueConstraint(
            "name", "user_id", "type", "uq_user_categories_name_user_type"
        ),
    )


class Operation(Base):
    type: Mapped[OperationType] = mapped_column()
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=2))
    date: Mapped[dt.date] = mapped_column(server_default=func.current_date())
    description: Mapped[str|None] = mapped_column(String(255), nullable=True)
    ignore: Mapped[bool] = mapped_column(server_default="false")

    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE")
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_categories.id", ondelete="CASCADE")
    )
    chain_id: Mapped[uuid.UUID|None] = mapped_column(
        ForeignKey("chains.id", ondelete="SET NULL"),
        nullable=True
    )
