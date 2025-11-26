from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, func

from src.database.base import Base

class User(Base):
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
