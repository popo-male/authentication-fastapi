from contextvars import ContextVar
from typing import Any, Dict, Optional

from pydantic import BaseModel


class RequestContext(BaseModel):
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    http_method: Optional[str] = None
    user_id: Optional[str] = None
    response_body: Optional[Dict[Any, Any]] = None


var_request_context: ContextVar[RequestContext] = ContextVar(
    "request_context",
    default=RequestContext(),
)


def get_request_id() -> str:
    return var_request_context.get().request_id
