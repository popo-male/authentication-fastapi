from fastapi import APIRouter

from app.api.responses import ResponseModel, response_helper

router = APIRouter()


@router.get("/", response_model=ResponseModel[dict])
async def list_resources():
    """Template list endpoint. Replace with module-specific logic."""
    return response_helper(data={"items": [], "total": 0})


@router.get("/{resource_id}", response_model=ResponseModel[dict])
async def get_resource(
    resource_id: str,
):
    """Template detail endpoint. Replace with module-specific logic."""
    return response_helper(data={"id": resource_id})
