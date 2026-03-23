from decimal import Decimal
import uuid

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey, UniqueConstraint, Numeric, Index

from src.database.base import Base
from src.common.enums import AccountType, Currency

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

    user: Mapped["User"] = relationship("User", back_populates="accounts")
    operations: Mapped[list["Operation"]] = relationship(
        back_populates="account"
    )

    __table_args__ = (
        UniqueConstraint(
            "name", "user_id", "is_active",
            name="uq_accounts_name_user_is_active"
        ),
        Index("idx_user_is_active", "user_id", "is_active"),
    )
