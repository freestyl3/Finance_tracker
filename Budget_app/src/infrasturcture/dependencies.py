from src.database.db_helper import db_helper
from src.infrasturcture.uow import UnitOfWork
from src.infrasturcture.repositories import repo_registry

async def get_uow():
    uow = UnitOfWork(
        session_factory=db_helper.session_factory,
        repo_registry=repo_registry
    )

    await uow.start()
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise
    finally:
        await uow.close()