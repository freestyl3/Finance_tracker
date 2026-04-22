from src.core.exceptions import DomainException

class SameAccountTransferError(DomainException):
    def __init__(self, message="Can't create transfer in the same account"):
        super().__init__(status_code=400, message=message)

class DifferentCurrencyInTransferError(DomainException):
    def __init__(self, message="Can't create transfer in accounts with different currency"):
        super().__init__(status_code=400, message=message)

class TransferIsOperationError(DomainException):
    def __init__(self, message="Can't edit operation on this endpoint. Use PATCH /operations/{operation_id}"):
        super().__init__(status_code=403, message=message)

class TransferNotFoundError(DomainException):
    def __init__(self, message="Transfer not found"):
        super().__init__(status_code=404, message=message)
