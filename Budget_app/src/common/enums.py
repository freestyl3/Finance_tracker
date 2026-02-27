from enum import Enum

class OperationType(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class AccountType(Enum):
    DEBIT = "debit"
    CASH = "cash"


class Currency(Enum):
    RUB = "rub"
