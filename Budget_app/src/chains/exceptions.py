from src.core.exceptions import DomainException

class NotEnoughOperationsForChainError(DomainException):
    def __init__(self, message="Can't create chain with less than 2 operations"):
        super().__init__(status_code=400, message=message)

class OperationsConflictError(DomainException):
    def __init__(self, message="Some operations not found or already in other chain"):
        super().__init__(status_code=409, message=message)

class TransferNotAllowedInChainError(DomainException):
    def __init__(self, message="Transfer can't be in chain"):
        super().__init__(status_code=400, message=message)

class ChainNotFoundError(DomainException):
    def __init__(self, message="Chain not found"):
        super().__init__(status_code=404, message=message)