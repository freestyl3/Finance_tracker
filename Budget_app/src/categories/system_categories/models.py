from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String

from src.categories.base.models import BaseCategory

class SystemCategory(BaseCategory):
    __tablename__ = "sys_categories"

    name: Mapped[str] = mapped_column(String(255), unique=True)
