import uuid
import uuid6

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from src.operations.models import Operation
from src.operations.schemas import TransferCreate, TransferUpdate

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
    
    async def get_related_operation(
            self,
            related_operation_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Operation:
        query = select(Operation).where(
            Operation.id == related_operation_id,
            Operation.user_id == user_id           
        ).options(joinedload(Operation.account), joinedload(Operation.category))

        result = await self.session.scalars(query)
        return result.unique().one_or_none()
    
    async def update(
            self,
            operation_from: Operation,
            operation_to: Operation,
            update_data: TransferUpdate
    ) -> list[Operation]:
        amount = update_data.amount
        account_from_id = update_data.account_from_id
        account_to_id = update_data.account_to_id

        update_data.amount = None
        update_data.account_from_id = None
        update_data.account_to_id = None

        dumped_data = update_data.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        for key, value in dumped_data.items():
            setattr(operation_from, key, value)
            setattr(operation_to, key, value)

        if amount:
            operation_from.amount = -amount
            operation_to.amount = amount

        if account_from_id:
            operation_from.account_id = account_from_id

        if account_to_id:
            operation_to.account_id = account_to_id
        
        await self.session.commit()
        await self.session.refresh(operation_from)
        await self.session.refresh(operation_to)

        return [operation_from, operation_to]
