import re

import asyncpg
from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.api.responses import ErrorDetail, ResponseClass, response_helper


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> ResponseClass:
    response_payload = response_helper(
        error=ErrorDetail(
            status_code=exc.status_code,
            detail=exc.detail,
        ),
    )
    return ResponseClass(
        status_code=exc.status_code,
        content=response_payload.model_dump(
            mode="json",
        ),
    )
                                               

async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> ResponseClass:
    logger.bind(
        error_code=500,
        error_message=str(exc),
    ).exception("An unhandled exception occurred")

    response_payload = response_helper(
        error=ErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unhandled Exception",
        ),
    )
    return ResponseClass(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_payload.model_dump(
            mode="json",
        ),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> ResponseClass:
    errors = [
        {
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "type": error.get("type"),
            "input": error.get("input"),
        }
        for error in exc.errors()
    ]
    response_payload = response_helper(
        error=ErrorDetail(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Validation Error",
            errors=errors,
        ),
    )
    return ResponseClass(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_payload.model_dump(
            mode="json",
        ),
    )


async def integrity_error_handler(
    request: Request,
    exc: IntegrityError,
):
    status_code = status.HTTP_409_CONFLICT
    detail = "Database integrity error occurred."

    if hasattr(exc, "orig"):
        detail = re.sub(r"^<class '[^']*'>: ", "", str(exc.orig), count=1)
        detail = detail.replace("\n", " ").replace("\\", "")

    response_payload = response_helper(
        error=ErrorDetail(
            status_code=status_code,
            detail=detail,
        ),
    )
    return ResponseClass(
        status_code=status_code,
        content=response_payload.model_dump(mode="json"),
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
