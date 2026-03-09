from decimal import Decimal
import datetime as dt
import uuid

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey, Numeric, func, Index

from src.database.base import Base
from src.common.enums import OperationType

class Operation(Base):
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
        ForeignKey("user_categories.id", ondelete="CASCADE")
    )
    # chain_id: Mapped[uuid.UUID|None] = mapped_column(
    #     ForeignKey("chains.id", ondelete="SET NULL"),
    #     nullable=True
    # )
    
    category: Mapped["UserCategory"] = relationship(
        back_populates="operations",
        lazy="joined"
    )
    account: Mapped["Account"] = relationship(
        back_populates="operations",
        lazy="joined"
    )

    __table_args__ = (Index("idx_user_id_id", "user_id", "id"), )
