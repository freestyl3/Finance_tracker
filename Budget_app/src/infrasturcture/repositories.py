from src.auth.repository import UserRepository
from src.categories.user_categories.repository import UserCategoryRepository

repo_registry = {
    UserRepository: UserRepository,
    UserCategoryRepository: UserCategoryRepository
}
