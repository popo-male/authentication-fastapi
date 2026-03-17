import json

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from loguru import logger

from app.api.responses import ErrorDetail, ResponseClass, response_helper


async def http_exception_handler(
    request: Request,
    exc: Exception,
) -> ResponseClass:
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Unhandled Exception"

    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        # FastAPI allows detail to be any JSON-serializable value.
        # Normalize to str to match ErrorDetail schema.
        if isinstance(exc.detail, str):
            detail = exc.detail
        else:
            detail = json.dumps(exc.detail)

    response_payload = response_helper(
        error=ErrorDetail(
            status_code=status_code,
            detail=detail,
        ),
    )
    return ResponseClass(
        status_code=status_code,
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
    exc: Exception,
) -> ResponseClass:
    errors = []
    if isinstance(exc, RequestValidationError):
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


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
