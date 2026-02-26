from decimal import Decimal
from enum import Enum
import datetime as dt
import uuid

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, ForeignKey, UniqueConstraint, Numeric, func

from database.base import Base


class OperationType(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


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
