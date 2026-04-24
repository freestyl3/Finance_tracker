from src.core.exceptions import DomainException

class AccountAlreadyExistsError(DomainException):
    def __init__(
            self,
            message="Active account with this name, type and currency already exists"
    ):
        super().__init__(message=message, status_code=409)


class AccountNotFoundError(DomainException):
    def __init__(
            self,
            message="Account not found"
    ):
        super().__init__(message=message, status_code=404)
