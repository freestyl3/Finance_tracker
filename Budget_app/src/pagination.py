from fastapi import Query

class PaginationParams:
    def __init__(
        self,
        limit: int = Query(default=10, ge=1, le=200, description="Количество записей"),
        offset: int = Query(default=0, ge=0, description="Смещение")
    ):
        self.limit = limit
        self.offset = offset