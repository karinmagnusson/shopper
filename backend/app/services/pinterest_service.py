"""Pinterest API v5 service with OAuth PKCE, rate limiting, and pagination."""

import base64
import hashlib
import logging
import os
import time
from typing import Any
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.core.security import decrypt_token, encrypt_token
from app.utils.cache import board_cache_key, cache_get, cache_set, pins_cache_key

logger = logging.getLogger(__name__)

PINTEREST_BASE = "https://api.pinterest.com/v5"
PINTEREST_AUTH_URL = "https://www.pinterest.com/oauth"
PINTEREST_TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"

SCOPES = "boards:read,pins:read,user_account:read"


def _generate_code_verifier() -> str:
    """Generate a PKCE code verifier (43-128 chars, URL-safe)."""
    return base64.urlsafe_b64encode(os.urandom(40)).rstrip(b"=").decode()


def _generate_code_challenge(verifier: str) -> str:
    """Derive a PKCE S256 code challenge from the verifier."""
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


class PinterestService:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=15.0)
        # Simple in-memory token bucket per Pinterest user (supplementary to Redis)
        self._request_counts: dict[str, list[float]] = {}

    # ------------------------------------------------------------------
    # OAuth helpers
    # ------------------------------------------------------------------

    def get_auth_url(self, state: str) -> tuple[str, str]:
        """
        Build the Pinterest OAuth authorisation URL with PKCE.

        Returns (url, code_verifier) — the verifier must be stored in the
        session so it can be used during the callback exchange.
        """
        verifier = _generate_code_verifier()
        challenge = _generate_code_challenge(verifier)
        params = {
            "client_id": settings.PINTEREST_CLIENT_ID,
            "redirect_uri": settings.PINTEREST_REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPES,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        return f"{PINTEREST_AUTH_URL}?{urlencode(params)}", verifier

    async def exchange_code_for_token(
        self, code: str, code_verifier: str
    ) -> dict[str, Any]:
        """Exchange an authorisation code for access + refresh tokens."""
        credentials = base64.b64encode(
            f"{settings.PINTEREST_CLIENT_ID}:{settings.PINTEREST_CLIENT_SECRET}".encode()
        ).decode()

        response = await self._client.post(
            PINTEREST_TOKEN_URL,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.PINTEREST_REDIRECT_URI,
                "code_verifier": code_verifier,
            },
        )
        response.raise_for_status()
        return response.json()

    async def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Use a refresh token to obtain a new access token."""
        credentials = base64.b64encode(
            f"{settings.PINTEREST_CLIENT_ID}:{settings.PINTEREST_CLIENT_SECRET}".encode()
        ).decode()

        response = await self._client.post(
            PINTEREST_TOKEN_URL,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        )
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # API helpers
    # ------------------------------------------------------------------

    def _check_rate_limit(self, user_id: str) -> None:
        """Simple in-process rate-limit guard (1 000 req / hour)."""
        now = time.time()
        window_start = now - settings.RATE_LIMIT_WINDOW
        calls = self._request_counts.setdefault(user_id, [])
        # Drop old timestamps
        self._request_counts[user_id] = [t for t in calls if t > window_start]
        if len(self._request_counts[user_id]) >= settings.RATE_LIMIT_REQUESTS:
            raise RuntimeError("Pinterest API rate limit exceeded")
        self._request_counts[user_id].append(now)

    async def _get(
        self, endpoint: str, access_token: str, params: dict | None = None
    ) -> dict[str, Any]:
        """Authenticated GET request to Pinterest API with retry on 429."""
        for attempt in range(3):
            response = await self._client.get(
                f"{PINTEREST_BASE}{endpoint}",
                headers={"Authorization": f"Bearer {access_token}"},
                params=params or {},
            )
            if response.status_code == 429:
                wait = int(response.headers.get("Retry-After", 5)) * (attempt + 1)
                logger.warning("Pinterest 429 – waiting %ss (attempt %s)", wait, attempt + 1)
                import asyncio
                await asyncio.sleep(wait)
                continue
            response.raise_for_status()
            return response.json()
        raise RuntimeError("Pinterest API rate limited after retries")

    # ------------------------------------------------------------------
    # User profile
    # ------------------------------------------------------------------

    async def get_user_profile(self, access_token: str) -> dict[str, Any]:
        return await self._get("/user_account", access_token)

    # ------------------------------------------------------------------
    # Boards
    # ------------------------------------------------------------------

    async def get_boards(
        self, user_id: str, access_token: str, page_size: int = 100
    ) -> list[dict[str, Any]]:
        """Fetch all boards for the authenticated user, with pagination + caching."""
        cache_key = board_cache_key(user_id)
        cached = await cache_get(cache_key)
        if cached:
            return cached

        self._check_rate_limit(user_id)
        boards: list[dict] = []
        bookmark: str | None = None

        while True:
            params: dict[str, Any] = {"page_size": page_size}
            if bookmark:
                params["bookmark"] = bookmark
            data = await self._get("/boards", access_token, params)
            boards.extend(data.get("items", []))
            bookmark = data.get("bookmark")
            if not bookmark:
                break

        await cache_set(cache_key, boards, ttl=900)
        return boards

    # ------------------------------------------------------------------
    # Pins
    # ------------------------------------------------------------------

    async def get_board_pins(
        self,
        user_id: str,
        board_id: str,
        access_token: str,
        page_size: int = 100,
    ) -> list[dict[str, Any]]:
        """Fetch all pins for a board with pagination + caching."""
        cache_key = pins_cache_key(board_id)
        cached = await cache_get(cache_key)
        if cached:
            return cached

        self._check_rate_limit(user_id)
        pins: list[dict] = []
        bookmark: str | None = None

        while True:
            params: dict[str, Any] = {"page_size": page_size}
            if bookmark:
                params["bookmark"] = bookmark
            data = await self._get(f"/boards/{board_id}/pins", access_token, params)
            pins.extend(data.get("items", []))
            bookmark = data.get("bookmark")
            if not bookmark:
                break

        await cache_set(cache_key, pins, ttl=1800)
        return pins


pinterest_service = PinterestService()
