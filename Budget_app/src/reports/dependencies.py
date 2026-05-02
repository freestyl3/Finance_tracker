from typing import Annotated

from fastapi import Depends

from src.core.uow import IUnitOfWork
from src.database.dependencies import get_uow
from src.reports.service import ReportService

async def get_report_service(
    uow: IUnitOfWork = Depends(get_uow)
) -> ReportService:
    return ReportService(uow)

ReportServiceDep = Annotated[
    ReportService,
    Depends(get_report_service)
]
