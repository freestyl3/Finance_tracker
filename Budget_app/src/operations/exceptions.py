from src.core.exceptions import DomainException

class OperationNotFoundError(DomainException):
    def __init__(self, message="Operation not found"):
        super().__init__(status_code=404, message=message)

class OperationInChainError(DomainException):
    def __init__(self, message="Can't edit operation inside chain. Remove operation from chain first"):
        super().__init__(status_code=403, message=message)

class OperationIsTransferError(DomainException):
    def __init__(self, message="Can't edit transfer on this endpoint. Use PATCH /transfers/{operation_id}"):
        super().__init__(status_code=403, message=message)
