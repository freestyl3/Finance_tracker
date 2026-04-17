from src.database.db_helper import db_helper
from src.database.uow import UnitOfWork

async def get_uow():
    uow = UnitOfWork(session_factory=db_helper.session_factory)

    await uow.start()
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise
    finally:
        await uow.close()