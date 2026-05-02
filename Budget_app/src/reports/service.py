import uuid
import datetime as dt
from decimal import Decimal
from typing import Literal

from src.core.uow import IUnitOfWork
from src.reports.repository import ReportRepository
from src.reports.filters import ReportFilter
from src.reports.schemas import ReportResponse, CategoryWithTotal, GroupedCategory
from src.common.enums import OperationType
from src.categories.user_categories.models import UserCategory
from src.feed.repository import FeedRepository

class ReportService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow
        
    @property
    def report_repo(self) -> ReportRepository:
        return self.uow.get_repo(ReportRepository)
    
    @property
    def feed_repo(self) -> FeedRepository:
        return self.uow.get_repo(FeedRepository)
    
    def segregate_data(
        self,
        grouped_data: list[tuple[UserCategory, float]]
    ) -> dict[Literal["incomes", "expenses"], CategoryWithTotal]:
        incomes = []
        expenses = []
        
        total_income = Decimal()
        total_expense = Decimal()

        for category, amount in grouped_data:
            grouped_item = GroupedCategory(
                category=category,
                amount=amount
            )
            
            if category.type == OperationType.INCOME:
                incomes.append(grouped_item)
                total_income += amount
            else:
                expenses.append(grouped_item)
                total_expense += amount

        return {
            "incomes": CategoryWithTotal(
                categories=incomes,
                total_amount=total_income
            ),
            "expenses": CategoryWithTotal(
                categories=expenses,
                total_amount=total_expense
            )
        }
        
    async def get_report(
        self,
        user_id: uuid.UUID,
        filters: ReportFilter
    ) -> ReportResponse:
        today = dt.date.today()

        if not filters.date_from and not filters.date_to:
            last_day, first_day = today, today - dt.timedelta(days=30)
            filters.date_from = first_day
            filters.date_to = last_day

        grouped_data = await self.report_repo.get_report(
            filters=filters,
            user_id=user_id
        )

        has_more = await self.feed_repo.get_max_date_before(
            user_id=user_id,
            before_date=filters.date_from
        )

        segregated_data = self.segregate_data(grouped_data)

        return ReportResponse(
            incomes=segregated_data["incomes"],
            expenses=segregated_data["expenses"],
            has_more=bool(has_more)
        )
