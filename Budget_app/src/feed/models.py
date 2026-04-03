import uuid
import datetime as dt
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import select, literal_column, union_all, String, Integer, null
from sqlalchemy.orm import Mapped, relationship

from src.database.base import Base
from src.operations.models import Operation
from src.chains.models import Chain

if TYPE_CHECKING:
    from src.accounts.models import Account
    from src.categories.user_categories.models import UserCategory

class FeedItemORM(Base):
    """
    Виртуальная (Read-Only) модель. Полная инкапсуляция по ООП.
    """

    __table__ = union_all(
        select(
            Operation.id,
            Operation.amount,
            Operation.date,
            Operation.description,
            Operation.ignore,
            Operation.account_id,
            Operation.category_id,
            Operation.user_id,
            literal_column("0", Integer).label("operations_count"),
            literal_column("'operation'", String).label("entry_type")
        ),
        select(
            Chain.id,
            Chain.amount,
            Chain.date,
            Chain.description,
            Chain.ignore,
            null().label("account_id"),
            Chain.category_id,
            Chain.user_id,
            Chain.operations_count,
            literal_column("'chain'", String).label("entry_type")
        )
    ).subquery("feed_view")

    __mapper_args__ = {
        "primary_key": [__table__.c.id]
    }

    id: Mapped[uuid.UUID]
    amount: Mapped[Decimal]
    date: Mapped[dt.date]
    description: Mapped[str | None]
    ignore: Mapped[bool]
    account_id: Mapped[uuid.UUID | None]
    category_id: Mapped[uuid.UUID | None]
    user_id: Mapped[uuid.UUID]
    operations_count: Mapped[int]
    entry_type: Mapped[str]

    account: Mapped["Account"] = relationship(
        "Account", 
        primaryjoin="FeedItemORM.account_id == Account.id",
        foreign_keys="[FeedItemORM.account_id]", 
        viewonly=True 
    )
    
    category: Mapped["UserCategory"] = relationship(
        "UserCategory", 
        primaryjoin="FeedItemORM.category_id == UserCategory.id",
        foreign_keys="[FeedItemORM.category_id]", 
        viewonly=True
    )
