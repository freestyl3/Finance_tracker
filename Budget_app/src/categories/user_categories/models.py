import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String
from sqlalchemy import ForeignKey, UniqueConstraint, Index

from src.categories.base.models import BaseCategory

class UserCategory(BaseCategory):
    __tablename__ = "user_categories"

    name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(server_default="true")
    deletable: Mapped[bool] = mapped_column(server_default="true")

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    operations: Mapped[list["Operation"]] = relationship(
        back_populates="category",
        lazy="joined"
    )

    __table_args__ = (
        UniqueConstraint(
            "name", "user_id", "type", name="uq_user_categories_name_user_type"
        ),
        Index("idx_user_type_is_active", "user_id", "type", "is_active"),
        Index("idx_user_name_type", "user_id", "name", "type")
    )
