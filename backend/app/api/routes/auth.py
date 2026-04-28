"""Pinterest OAuth endpoints."""

import logging
import secrets
import uuid

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DBSession
from app.core.security import create_access_token, decrypt_token, encrypt_token
from app.models.user import User
from app.services.pinterest_service import pinterest_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/pinterest")
async def pinterest_auth_url(request: Request) -> JSONResponse:
    """Generate a Pinterest OAuth URL with PKCE and a CSRF state token."""
    state = secrets.token_urlsafe(32)
    auth_url, code_verifier = pinterest_service.get_auth_url(state)

    # Store verifier + state in the session (simple cookie-based via starlette)
    request.session["oauth_state"] = state
    request.session["code_verifier"] = code_verifier

    return JSONResponse({"auth_url": auth_url, "state": state})


@router.get("/callback")
async def pinterest_callback(
    code: str = Query(...),
    state: str = Query(...),
    request: Request = None,
    db: AsyncSession = DBSession,
) -> JSONResponse:
    """
    Handle Pinterest OAuth callback.

    Exchanges the authorisation code for tokens, upserts the user record,
    and returns a signed JWT.
    """
    stored_state = request.session.get("oauth_state")
    code_verifier = request.session.get("code_verifier")

    if not stored_state or stored_state != state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")
    if not code_verifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing PKCE code verifier"
        )

    try:
        token_data = await pinterest_service.exchange_code_for_token(code, code_verifier)
    except Exception as exc:
        logger.error("Token exchange failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to exchange code with Pinterest",
        ) from exc

    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")

    try:
        profile = await pinterest_service.get_user_profile(access_token)
    except Exception as exc:
        logger.error("Failed to fetch Pinterest profile: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch user profile from Pinterest",
        ) from exc

    pinterest_id: str = profile.get("id") or profile.get("username", "")
    email: str | None = profile.get("email")

    result = await db.execute(select(User).where(User.pinterest_id == pinterest_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            id=uuid.uuid4(),
            pinterest_id=pinterest_id,
            email=email,
            access_token_encrypted=encrypt_token(access_token),
            refresh_token_encrypted=encrypt_token(refresh_token) if refresh_token else None,
        )
        db.add(user)
    else:
        user.access_token_encrypted = encrypt_token(access_token)
        if refresh_token:
            user.refresh_token_encrypted = encrypt_token(refresh_token)
        if email:
            user.email = email

    await db.commit()
    await db.refresh(user)

    # Clear session PKCE data
    request.session.pop("oauth_state", None)
    request.session.pop("code_verifier", None)

    jwt_token = create_access_token(str(user.id))
    return JSONResponse({"access_token": jwt_token, "token_type": "bearer"})


@router.post("/refresh")
async def refresh_token(current_user: CurrentUser, db: DBSession) -> JSONResponse:
    """Refresh the Pinterest access token and return a new JWT."""
    if not current_user.refresh_token_encrypted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No refresh token stored"
        )

    try:
        refresh_token_plain = decrypt_token(current_user.refresh_token_encrypted)
        token_data = await pinterest_service.refresh_access_token(refresh_token_plain)
    except Exception as exc:
        logger.error("Token refresh failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to refresh Pinterest token"
        ) from exc

    current_user.access_token_encrypted = encrypt_token(token_data["access_token"])
    new_refresh = token_data.get("refresh_token")
    if new_refresh:
        current_user.refresh_token_encrypted = encrypt_token(new_refresh)

    await db.commit()
    jwt_token = create_access_token(str(current_user.id))
    return JSONResponse({"access_token": jwt_token, "token_type": "bearer"})


@router.delete("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, current_user: CurrentUser) -> None:
    """Clear the server-side session (client should discard the JWT)."""
    request.session.clear()
