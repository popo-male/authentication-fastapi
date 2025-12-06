from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.core.context import var_request_context

T = TypeVar("T")


class ErrorDetail(BaseModel):
    status_code: int
    detail: str
    errors: Optional[List[Dict[str, Any]]] = None


# data field can be any type(T) for success response
class ResponseModel(BaseModel, Generic[T]):
    request_id: str
    timestamp: datetime
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None

    # example JSON show in OpenAPI docs
    model_config = ConfigDict(
        json_schema_extra={
            "example_success": {
                "request_id": "uuid-goes-here",
                "timestamp": "2023-01-01T12:00:00Z",
                "data": {"message": "Success payload"},
                "error": None,
            },
            "example_error": {
                "request_id": "uuid-goes-here",
                "timestamp": "2023-01-01T12:00:00Z",
                "data": None,
                "error": {
                    "status_code": 404,
                    "detail": "Resource not found",
                    "errors": None,
                },
            },
        }
    )


class ResponseClass(JSONResponse):
    def render(self, content):
        context = var_request_context.get()
        context.response_body = content
        return super().render(content)


def response_helper(data: Any = None, error: Any = None) -> ResponseModel:
    """
    Helper that populates request id and timestamp for you.

    You can simply return ResponseModel(), with request_id
    and timestamp populated accordingly.
    """
    context = var_request_context.get()
    return ResponseModel(
        request_id=context.request_id,
        timestamp=datetime.now().isoformat(),
        data=data if data else None,
        error=error if error else None,
    )
