from src.core.exceptions import DomainException

class UserAlreadyExistsError(DomainException):
    def __init__(self, message="User with this username or email already exists"):
        super().__init__(message=message, status_code=409)
