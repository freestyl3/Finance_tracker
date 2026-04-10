from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.exceptions import DomainException

async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(DomainException, domain_exception_handler)
1