from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from src.database.base import AbstractOperation, CategoryBase

if TYPE_CHECKING:
    from src.auth.models import User

class IncomeCategory(CategoryBase):
    incomes: Mapped[list["Income"]] = relationship(back_populates="category")


class Income(AbstractOperation):
    user: Mapped["User"] = relationship(back_populates="incomes")

    category_id: Mapped[int] = mapped_column(
        ForeignKey("incomecategory.id", ondelete="CASCADE")
    )
    category: Mapped["IncomeCategory"] = relationship(
        back_populates="incomes",
        lazy="joined"
    )
