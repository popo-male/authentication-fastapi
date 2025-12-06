import json
import logging

from loguru import logger

from app.core.config import settings
from app.core.context import var_request_context


class InterceptHandler(logging.Handler):
    """
    Custom logging handler to intercept standard logging messages
    and redirect them to loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def patch_record_with_json(record: dict) -> None:
    """
    Patcher that replaces the log message with a structured JSON payload.
    """
    context = var_request_context.get()
    log_payload = {
        "timestamp": record["time"].isoformat(),
        "log_level": record["level"].name,
        "log_message": record["message"],
        "module": settings.APP_NAME,
        "layer": settings.APP_LAYER,
        "environment": settings.APP_ENVIRONMENT,
        "component": record["name"],
        "request_id": context.request_id,
        "endpoint": context.endpoint,
        "http_method": context.http_method,
        "user_id": context.user_id,
        # Always null (compat only)
        "error_code": None,
        "error_message": None,
    }

    # If extra data was bound to the logger, merge it into the payload.
    # This allows logger.bind(key="value").info(...) to work seamlessly.
    log_payload.update(record["extra"])

    # Overwrite the original message with the JSON string
    record["message"] = json.dumps(log_payload)


def setup_logging():
    # Remove any default handlers
    logger.remove()
    # Patch the logger to use our JSON structuring function
    # All log messages will now pass through patch_record_with_json
    logger.configure(patcher=patch_record_with_json)

    logger.add(
        sink=settings.LOG_FILE_PATH,
        level=settings.LOG_LEVEL.upper(),
        format="{message}",
        serialize=False,
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )

    # disable uvicorn log
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.disabled = True
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.disabled = True

    # authlib log
    authlib_logger = logging.getLogger("authlib")
    authlib_logger.setLevel(logging.INFO)

    # urllib3
    urllib3_logger = logging.getLogger("urllib3")
    urllib3_logger.setLevel(logging.WARNING)

    # intercept standard log
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
