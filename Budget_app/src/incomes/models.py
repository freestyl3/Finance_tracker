from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from src.database.base import OperationBase, CategoryBase

if TYPE_CHECKING:
    from src.auth.models import User

class IncomeCategory(CategoryBase):
    incomes: Mapped[list["Income"]] = relationship(back_populates="category")


class Income(OperationBase):
    user: Mapped["User"] = relationship(back_populates="income")

    category_id: Mapped[int] = mapped_column(ForeignKey("incomecategory.id"))
    category: Mapped["IncomeCategory"] = relationship(
        back_populates="incomes",
        lazy="joined"
    )
