import uuid
from typing import Generic, TypeVar

from sqlalchemy.exc import IntegrityError

from src.base.repository import (
    BaseRepository, ActiveNamedRepository, ModelType, UpdateSchemaType
)

### ПЕРЕПИСАТЬ НА КАСТОМНЫЕ ИСКЛЮЧЕНИЯ И ОБРАБОТЧИКИ

RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)
ActiveNamedRepositoryType = TypeVar(
    "ActiveNamedRepositoryType",
    bound=ActiveNamedRepository
)

class BaseService(Generic[RepositoryType]):
    def __init__(self, repo: BaseRepository):
        self.repo = repo

    async def get_by_id(
            self,
            model_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> ModelType | None:
        return await self.repo.get_by_id(model_id, user_id)
    
    async def get_all(self, user_id: uuid.UUID) -> list[ModelType]:
        return list(await self.repo.get_all(user_id))
    
    async def update(
            self,
            model_id: uuid.UUID,
            model_update: UpdateSchemaType,
            user_id: uuid.UUID
    ) -> ModelType | None:
        try:
            updated = await self.repo.update(model_id, model_update, user_id)

            if not updated:
                raise ValueError(f"{self.repo.model.__name__} not found")
            
            await self.repo.session.commit()
            await self.repo.session.refresh(updated)
        
            return updated
        except IntegrityError as e:
            raise ValueError(str(e))
        
    async def delete(
            self,
            model_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool | None:
        result = await self.repo.delete(model_id, user_id)
        await self.repo.session.commit()

        return result

class ActiveNamedService(BaseService[ActiveNamedRepositoryType]):
    def __init__(self, repo: ActiveNamedRepository):
        self.repo = repo

    async def get_by_id(
            self,
            model_id: uuid.UUID,
            user_id: uuid.UUID,
            only_active: bool = True
    ) -> ModelType | None:
        return await self.repo.get_by_id(model_id, user_id, only_active)
    
    async def get_by_name(
            self,
            model_name: str,
            user_id: uuid.UUID,
            only_active: bool = True
    ) -> ModelType | None:
        return await self.repo.get_by_name(model_name, user_id, only_active)
    
    async def get_all(
            self,
            user_id: uuid.UUID,
            only_active: bool = True
    ) -> list[ModelType]:
        return list(await self.repo.get_all(user_id, only_active))
    
    async def soft_delete(
            self,
            model_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool | None:
        result = await self.repo.soft_delete(model_id, user_id)

        if not result:
            raise ValueError(f"{self.repo.model.__name__} not found")
        
        await self.repo.session.commit()
        return result

# class BaseOperationService:
#     def __init__(self, repo: BaseOperationRepository):
#         self.repo = repo

#     async def create(
#             self,
#             user_id: int,
#             create_data: OperationCreate
#     ):
#         try:
#             new_operation = await self.repo.create(
#                 operation_data=create_data,
#                 user_id=user_id
#             )
#         except ValueError as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=str(e)
#             )

#         return new_operation

#     async def get_all(
#             self,
#             user_id: int,
#             filters: OperationFilterBase, 
#             pagination: PaginationParams
#     ):
#         return await self.repo.get_operations(user_id, filters, pagination)
    
#     async def update(
#             self,
#             operation_id: int,
#             update_data: OperationUpdate,
#             user_id: int
#     ):
#         try:
#             updated_operation = await self.repo.update_operation(
#                 operation_id,
#                 user_id,
#                 update_data
#             )
#         except ValueError as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=str(e)
#             )

#         if not updated_operation:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Operation not found or you don't have permission."
#             )
        
#         return updated_operation
    
#     async def delete(self, operation_id: int, user_id: int):
#         is_deleted = await self.repo.delete_operation(operation_id, user_id)

#         if not is_deleted:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Operation not found or you don't have permission."
#             )

#         return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    # async def get_operations_stats(self, user_id: int, filters: ReportFilter):
    #     check_date_order(filters)
    #     return await self.repo.get_operations_stats(user_id, filters)
    
    # async def get_operations_report(self, user_id: int, filters: ReportFilter):
    #     check_date_order(filters)
    #     report_data = await self.repo.get_operations_stats(
    #         user_id=user_id,
    #         filter_params=filters
    #     )

    #     csv_file = generate_csv_report(report_data)

    #     filename = f"report_{filters.date_from}_{filters.date_to}.csv"

    #     return csv_file, filename

    # async def get_monthly_operations(
    #     self,
    #     year: int | None,
    #     month: int | None,
    #     user_id: int
    # ):
    #     today = date.today()
    #     target_year = year if year else today.year
    #     target_month = month if month else today.month

    #     first_day, last_day = get_month_range(target_year, target_month)

    #     filters = ReportFilter(
    #         date_from=first_day,
    #         date_to=last_day
    #     )

    #     return await self.get_operations_stats(user_id, filters)
