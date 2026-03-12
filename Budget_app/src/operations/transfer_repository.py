import uuid
import uuid6

from sqlalchemy.ext.asyncio import AsyncSession

from src.operations.models import Operation
from src.operations.schemas import TransferCreate

class TransferRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
            self,
            transfer_data: TransferCreate,
            transfer_category_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> list[Operation]:
        from_id = uuid6.uuid7()
        to_id = uuid6.uuid7()

        operation_from = Operation(
            id=from_id,
            amount=-transfer_data.amount,
            date=transfer_data.date,
            description=transfer_data.description,
            account_id=transfer_data.account_from,
            category_id=transfer_category_id,
            related_operation_id=to_id,
            user_id=user_id
        )

        operation_to = Operation(
            id=to_id,
            amount=transfer_data.amount,
            date=transfer_data.date,
            description=transfer_data.description,
            account_id=transfer_data.account_to,
            category_id=transfer_category_id,
            related_operation_id=from_id,
            user_id=user_id
        )

        self.session.add_all([operation_from, operation_to])
        await self.session.commit()
        
        return [operation_from, operation_to]
