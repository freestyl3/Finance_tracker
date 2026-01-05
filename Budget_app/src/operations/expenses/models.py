from typing import TYPE_CHECKING

from src.database.base import AbstractOperation
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from src.database.base import CategoryBase

if TYPE_CHECKING:
    from src.auth.models import User

class ExpenseCategory(CategoryBase):
    expenses: Mapped[list["Expense"]] = relationship(back_populates="category")


class Expense(AbstractOperation):
    user: Mapped["User"] = relationship(back_populates="expenses")

    category_id: Mapped[int] = mapped_column(
        ForeignKey("expensecategory.id", ondelete="CASCADE")
    )
    category: Mapped[ExpenseCategory] = relationship(
        back_populates="expenses",
        lazy="joined"
    )
