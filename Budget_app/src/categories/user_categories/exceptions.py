from src.core.exceptions import DomainException

class UserCategoryAlreadyExistsError(DomainException):
    def __init__(self, message="User category already exists"):
        super().__init__(status_code=409, message=message)

class UserCategoryNotFoundError(DomainException):
    def __init__(self, message="User category not found"):
        super().__init__(status_code=404, message=message)

class UserCategoryTypeMismatchError(DomainException):
    def __init__(self, message="User category type mismatch"):
        super().__init__(status_code=400, message=message)
