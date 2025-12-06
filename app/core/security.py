import logging
from typing import Optional
from authlib.jose import JoseError, jwt
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from pydantic import ValidationError
from app.schemas.token import TokenPayload
from app.schemas.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)

# auto_error=False allows to handle missing tokens manually
bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(user: User) -> str:
    """Create a JWT access token."""
    expire = datetime.now() + timedelta(minutes=settings.APP_JWT_EXPIRY_MINUTES)

    claims = {
        "exp": expire,
        "iat": datetime.now(),
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    }

    header = {"alg": settings.APP_JWT_ALGORITHM}
    return jwt.encode(
        header,
        claims,
        settings.APP_SESSION_SECRET_KEY,
    )


def decode_access_token(token: str):
    """Decode a JWT access token."""
    payload = jwt.decode(token, settings.APP_SESSION_SECRET_KEY)
    payload.validate()
    return payload


async def try_get_token(request: Request) -> Optional[TokenPayload]:
    auth: HTTPAuthorizationCredentials = await bearer_scheme(request)
    token = None

    # first try get from header
    if auth is not None:
        token = auth.credentials

    # try get from cookie
    if token is None:
        token = request.cookies.get("access_token")

    if token is None:
        return None

    try:
        payload = decode_access_token(token)
        return TokenPayload(**payload)
    except (JoseError, ValidationError) as e:
        logger.error("Token validation or decode error:", exc_info=e)
        return None


# dependency to protect routes
async def get_current_user(
    request: Request, auth: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    """Decode JWT token and retrieve current user information."""
    token_payload = await try_get_token(request)
    if token_payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return token_payload
