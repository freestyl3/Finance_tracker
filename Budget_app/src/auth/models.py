from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, func

from src.database.base import Base

class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_admin: Mapped[bool] = mapped_column(
        server_default="FALSE",
        nullable=False
    )
    is_staff: Mapped[bool] = mapped_column(
        server_default="FALSE",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    accounts: Mapped[list["Account"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
