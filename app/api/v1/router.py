from enum import Enum
from typing import cast

from fastapi import APIRouter

from app.api.v1.endpoints import base


def create_v1_router() -> APIRouter:
    router = APIRouter(prefix="/v1")
    module_registry = [
        (base.router, "/system", ["system"]),
    ]

    for module_router, prefix, tags in module_registry:
        router.include_router(
            module_router,
            prefix=prefix,
            tags=cast(list[str | Enum], tags),
        )

    return router


router = create_v1_router()
