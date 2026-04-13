from src.auth.repository import UserRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.accounts.repository import AccountRepository
from src.operations.repositories.repository import OperationRepository

repo_registry = {
    UserRepository: UserRepository,
    UserCategoryRepository: UserCategoryRepository,
    AccountRepository: AccountRepository,
    OperationRepository: OperationRepository
}
