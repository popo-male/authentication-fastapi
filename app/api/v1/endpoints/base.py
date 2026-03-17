from fastapi import APIRouter

from app.api.responses import ResponseModel, response_helper

router = APIRouter()


@router.get("/ping", response_model=ResponseModel[dict])
async def ping():
    return response_helper(data={"message": "pong"})
