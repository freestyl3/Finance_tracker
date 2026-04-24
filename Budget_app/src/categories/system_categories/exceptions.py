from src.core.exceptions import DomainException

class SystemCategoryAlreadyExistsError(DomainException):
    def __init__(self, message="System category already exists"):
        super().__init__(status_code=409, message=message)

class SystemCategoryNotFoundError(DomainException):
    def __init__(self, message="System category not found"):
        super().__init__(status_code=404, message=message)
