import uuid
import datetime as dt
from decimal import Decimal

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey, Numeric, func

from src.database.base import Base

class Chain(Base):
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=2))
    date: Mapped[dt.date] = mapped_column(server_default=func.current_date())
    description: Mapped[str|None] = mapped_column(String(255), nullable=True)
    ignore: Mapped[bool] = mapped_column(server_default="false")

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE")
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_categories.id", ondelete="SET NULL"),
        nullable=True
    )
