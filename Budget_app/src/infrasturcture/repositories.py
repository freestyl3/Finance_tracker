from src.auth.repository import UserRepository
from src.categories.system_categories.repository import SystemCategoryRepository
from src.categories.user_categories.repository import UserCategoryRepository
from src.accounts.repository import AccountRepository
from src.operations.repositories.repository import OperationRepository

repo_registry = {
    UserRepository: UserRepository,
    SystemCategoryRepository: SystemCategoryRepository,
    UserCategoryRepository: UserCategoryRepository,
    AccountRepository: AccountRepository,
    OperationRepository: OperationRepository
}
