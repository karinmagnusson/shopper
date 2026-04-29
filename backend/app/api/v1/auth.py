import logging
import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.cache import cache_delete, cache_get, cache_set
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.services.pinterest import PinterestAPIError, PinterestService
from app.utils.rate_limiter import auth_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# Known OAuth error codes Pinterest may return.
# Any unrecognised code is replaced with "unknown" to prevent open-redirect payloads
# being reflected in the Location header.
_KNOWN_OAUTH_ERRORS = frozenset(
    {
        "access_denied",
        "invalid_scope",
        "invalid_request",
        "unsupported_response_type",
        "server_error",
        "temporarily_unavailable",
    }
)


def _safe_reason(raw: str) -> str:
    return raw if raw in _KNOWN_OAUTH_ERRORS else "unknown"


def _frontend_error_url(reason: str) -> str:
    base = settings.PINTEREST_REDIRECT_URI.replace("/auth/callback", "").rstrip("/")
    return f"{base}/auth/error?reason={_safe_reason(reason)}"


@router.get("/pinterest/login")
async def pinterest_login():
    """Redirect the user to Pinterest's OAuth consent screen."""
    state = secrets.token_urlsafe(32)
    cache_set(f"oauth_state:{state}", {"valid": True}, ttl=600)
    oauth_url = PinterestService.generate_oauth_url(state)
    return RedirectResponse(url=oauth_url, status_code=302)


@router.get("/pinterest/callback")
async def pinterest_callback(
    request: Request,
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
    db: Session = Depends(get_db),
):
    """Handle Pinterest OAuth callback, create/update user, return JWT."""
    if error:
        logger.warning("Pinterest OAuth error: %s", error)
        return RedirectResponse(url=_frontend_error_url(error))

    if not code or not state:
        return RedirectResponse(url=_frontend_error_url("invalid_request"))

    # Validate CSRF state
    state_key = f"oauth_state:{state}"
    stored = cache_get(state_key)
    if not stored:
        return RedirectResponse(url=_frontend_error_url("invalid_state"))
    cache_delete(state_key)

    # Rate-limit by IP
    client_ip = request.client.host if request.client else "unknown"
    allowed, _ = auth_limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")

    try:
        token_data = await PinterestService.exchange_code(code)
        user_profile = await PinterestService.get_user_profile(token_data["access_token"])
    except PinterestAPIError as exc:
        logger.error("Pinterest API error during callback: %s", exc)
        return RedirectResponse(url=_frontend_error_url("server_error"))

    # Upsert user
    pinterest_id = user_profile.get("id") or user_profile.get("username")
    user = db.query(User).filter(User.pinterest_id == pinterest_id).first()
    if not user:
        user = User(
            pinterest_id=pinterest_id,
            email=user_profile.get("email"),
            access_token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
        )
        db.add(user)
    else:
        user.access_token = token_data.get("access_token")
        user.refresh_token = token_data.get("refresh_token")
        if user_profile.get("email"):
            user.email = user_profile["email"]
    db.commit()
    db.refresh(user)

    jwt_token = create_access_token({"sub": str(user.id)})
    frontend_base = settings.PINTEREST_REDIRECT_URI.replace("/auth/callback", "").rstrip("/")
    return RedirectResponse(url=f"{frontend_base}/auth/callback?token={jwt_token}")


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "pinterest_id": current_user.pinterest_id,
        "email": current_user.email,
        "created_at": current_user.created_at,
        "last_sync": current_user.last_sync,
    }
