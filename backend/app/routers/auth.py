"""Auth router: Pinterest OAuth callback, logout, and current-user endpoint."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginResponse, OAuthCallbackRequest
from app.schemas.user import UserResponse
from app.services import auth_service, pinterest_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/pinterest/oauth", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def pinterest_oauth_callback(
    payload: OAuthCallbackRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Exchange a Pinterest OAuth code for a JWT access token.

    Flow:
      1. Exchange code → Pinterest access token.
      2. Fetch Pinterest user profile.
      3. Create or update local User record.
      4. Return signed JWT.
    """
    try:
        token_data = await pinterest_service.exchange_code_for_token(payload.code)
    except Exception as exc:
        logger.exception("Pinterest token exchange failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to exchange Pinterest OAuth code",
        ) from exc

    access_token: str = token_data.get("access_token", "")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="No access_token in Pinterest response")

    try:
        pinterest_user = await pinterest_service.get_pinterest_user(access_token)
    except Exception as exc:
        logger.exception("Failed to fetch Pinterest user profile")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve Pinterest user profile",
        ) from exc

    pinterest_id: str = pinterest_user.get("id") or pinterest_user.get("username", "")
    if not pinterest_id:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Pinterest user ID missing")

    # Upsert user
    result = await db.execute(select(User).where(User.pinterest_id == pinterest_id))
    user: User | None = result.scalar_one_or_none()

    if user is None:
        user = User(
            pinterest_id=pinterest_id,
            email=pinterest_user.get("email"),
            display_name=pinterest_user.get("username") or pinterest_user.get("full_name"),
            avatar_url=(pinterest_user.get("profile_image") or {}).get("original", {}).get("url"),
        )
        db.add(user)
        await db.flush()
        logger.info("Created new user pinterest_id=%s", pinterest_id)
    else:
        user.display_name = pinterest_user.get("username") or user.display_name
        user.email = pinterest_user.get("email") or user.email

    await db.commit()
    await db.refresh(user)

    jwt_token = auth_service.create_access_token(subject=str(user.id))
    return LoginResponse(
        access_token=jwt_token,
        expires_in=auth_service.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
        display_name=user.display_name,
        avatar_url=user.avatar_url,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(auth_service.get_current_user),
) -> None:
    """Invalidate the current session (client should discard the JWT).

    JWT tokens are stateless; the frontend clears its stored token.
    """
    # Stateless JWT: no server-side revocation in MVP.
    return None


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(auth_service.get_current_user),
) -> UserResponse:
    """Return the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)
