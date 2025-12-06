import json
import time
from typing import Optional
import uuid

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import Message

from app.core.context import RequestContext, var_request_context
from app.core.security import try_get_token


def _get_sanitized_headers(request: Request):
    SENSITIVE_HEADERS = {
        "authorization",
        "cookie",
        "proxy-authorization",
        "x-csrf-token",
    }

    ALLOWED_HEADERS = {
        "host",
        "user-agent",
        "content-type",
        "accept",
        "content-length",
        "x-request-id",
        "x-forwarded-for",
    }

    sanitized_headers = {}
    for key, value in request.headers.items():
        key_lower = key.lower()
        if key_lower in SENSITIVE_HEADERS:
            sanitized_headers[key] = "[REDACTED]"
        elif key_lower in ALLOWED_HEADERS:
            sanitized_headers[key] = value

    return sanitized_headers


async def get_request_body(request: Request):
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        return None

    try:
        body_bytes = await request.body()
        if not body_bytes:
            return None

        # Replace the body stream so the endpoint can still read it.
        async def receive() -> Message:
            return {"type": "http.request", "body": body_bytes}

        request._receive = receive
        return json.loads(body_bytes)
    except Exception:
        # If body is not valid JSON, cannot be read, etc., we log a warning
        # but proceed without a body in the logs.
        logger.warning("Could not read or parse request body.")
        return None


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Optional[Response]:
        """
        Middleware to log incoming requests and outgoing responses.
        """
        start_time = time.monotonic()
        request_id = str(uuid.uuid4())

        user_id = "N/A"
        token = await try_get_token(request)
        if token:
            user_id = token.email

        # Set context variables for this request
        var_request_context.set(
            RequestContext(
                request_id=request_id,
                endpoint=request.url.path,
                http_method=request.method,
                user_id=user_id,
            )
        )

        request_body = await get_request_body(request)
        logger.bind(
            http={
                "url": str(request.url),
                "method": request.method,
                "headers": _get_sanitized_headers(request),
                "client_host": request.client.host if request.client else "unknown",
                "request_body": request_body if request_body else None,
            }
        ).info("HTTP Request Start")

        response = None
        try:
            response = await call_next(request)
        finally:
            process_time = (time.monotonic() - start_time) * 1000
            ctx = var_request_context.get()
            response_body = ctx.response_body
            logger.bind(
                http={
                    "status_code": response.status_code if response else 500,
                    "duration_ms": round(process_time, 2),
                    "response_body": response_body if response_body else None,
                }
            ).info("HTTP Request Finish")

        return response
