"""Pinterest OAuth authentication endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from typing import Optional
import secrets
import httpx
from datetime import datetime, timedelta
from jose import jwt

from backend.config import settings

router = APIRouter()

# In-memory storage for OAuth state tokens (use Redis in production)
oauth_states = {}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


@router.get("/pinterest/login")
async def pinterest_login():
    """
    Initiate Pinterest OAuth flow.
    Redirects user to Pinterest authorization page.
    """
    # Generate random state token for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"created_at": datetime.utcnow()}
    
    # Pinterest OAuth 2.0 authorization URL
    # Scopes: boards:read, pins:read, user_accounts:read
    auth_url = (
        f"https://www.pinterest.com/oauth/?"
        f"client_id={settings.pinterest_app_id}&"
        f"redirect_uri={settings.pinterest_redirect_uri}&"
        f"response_type=code&"
        f"scope=boards:read,pins:read,user_accounts:read&"
        f"state={state}"
    )
    
    return RedirectResponse(url=auth_url)


@router.get("/pinterest/callback")
async def pinterest_callback(code: str, state: str):
    """
    Handle Pinterest OAuth callback.
    Exchange authorization code for access token.
    """
    # Verify state token
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state token")
    
    # Remove used state token
    del oauth_states[state]
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://api.pinterest.com/v5/oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.pinterest_redirect_uri,
            },
            auth=(settings.pinterest_app_id, settings.pinterest_app_secret),
        )
    
    if token_response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get access token: {token_response.text}"
        )
    
    token_data = token_response.json()
    pinterest_access_token = token_data.get("access_token")
    
    # Get user info from Pinterest
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://api.pinterest.com/v5/user_account",
            headers={"Authorization": f"Bearer {pinterest_access_token}"}
        )
    
    if user_response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Failed to get user information"
        )
    
    user_data = user_response.json()
    
    # Create our application's access token
    access_token = create_access_token(
        data={
            "sub": user_data.get("username"),
            "pinterest_token": pinterest_access_token,
            "user_id": user_data.get("id")
        }
    )
    
    # TODO: Store user and Pinterest token in database
    # For now, redirect to frontend with token
    # Try the built-in frontend first, fallback to configured frontend URL
    frontend_redirect = f"http://localhost:8000/app?token={access_token}"
    
    return RedirectResponse(url=frontend_redirect)


@router.get("/me")
async def get_current_user():
    """
    Get current authenticated user information.
    TODO: Implement JWT token verification and user lookup
    """
    return {
        "message": "User endpoint - to be implemented with JWT verification"
    }


@router.post("/logout")
async def logout():
    """Logout current user."""
    # TODO: Implement token invalidation
    return {"message": "Logged out successfully"}
