from enum import Enum

class RepoAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
