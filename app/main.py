from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.exceptions import register_exception_handlers
from app.api.responses import ResponseClass, response_helper
from app.api.v1.router import router
from app.core.config import settings
from app.core.logger import setup_logging
from app.middleware.logging import LoggingMiddleware

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    default_response_class=ResponseClass,
)

# exception handlers
register_exception_handlers(app)

# middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(SessionMiddleware, settings.APP_SESSION_SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# routers
app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return response_helper(
        data={
            "message": f"{settings.APP_NAME} running.",
        },
    )


@app.get("/health")
def get_health_status():
    return response_helper(
        data={
            "status": "ok",
        },
    )
