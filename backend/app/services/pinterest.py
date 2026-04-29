import logging
import urllib.parse

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class PinterestAPIError(Exception):
    pass


class PinterestService:
    BASE = "https://api.pinterest.com/v5"
    TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"

    @staticmethod
    def generate_oauth_url(state: str) -> str:
        params = {
            "client_id": settings.PINTEREST_APP_ID,
            "redirect_uri": settings.PINTEREST_REDIRECT_URI,
            "response_type": "code",
            "scope": "boards:read,pins:read,user_accounts:read",
            "state": state,
        }
        return f"{settings.pinterest_oauth_url}?{urllib.parse.urlencode(params)}"

    @staticmethod
    async def exchange_code(code: str) -> dict:
        """Exchange auth code for access token."""
        if not settings.PINTEREST_APP_ID:
            # Mock for development
            return {
                "access_token": "mock_access_token",
                "refresh_token": "mock_refresh_token",
                "token_type": "bearer",
            }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                PinterestService.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.PINTEREST_REDIRECT_URI,
                },
                auth=(settings.PINTEREST_APP_ID, settings.PINTEREST_APP_SECRET),
            )
            if not resp.is_success:
                raise PinterestAPIError(f"Token exchange failed: {resp.text}")
            return resp.json()

    @staticmethod
    async def get_user_profile(access_token: str) -> dict:
        if access_token == "mock_access_token":
            return {"id": "mock_user_123", "username": "mock_user", "email": "mock@example.com"}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{PinterestService.BASE}/user_account",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if not resp.is_success:
                raise PinterestAPIError(f"Profile fetch failed: {resp.text}")
            return resp.json()

    @staticmethod
    async def get_user_boards(access_token: str) -> list[dict]:
        if access_token == "mock_access_token":
            return [
                {"id": "board_1", "name": "Fashion Inspo", "pin_count": 42, "description": "My style board"},
                {"id": "board_2", "name": "Minimalist Looks", "pin_count": 28, "description": "Clean aesthetic"},
                {"id": "board_3", "name": "Summer Vibes", "pin_count": 15, "description": "Summer fashion"},
            ]
        boards: list[dict] = []
        cursor = None
        while True:
            params: dict = {"page_size": 25}
            if cursor:
                params["bookmark"] = cursor
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{PinterestService.BASE}/boards",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params=params,
                )
                if not resp.is_success:
                    raise PinterestAPIError(f"Boards fetch failed: {resp.text}")
                data = resp.json()
                boards.extend(data.get("items", []))
                cursor = data.get("bookmark")
                if not cursor:
                    break
        return boards

    @staticmethod
    async def get_board_pins(access_token: str, board_id: str) -> list[dict]:
        if access_token == "mock_access_token":
            return [
                {
                    "id": f"pin_{board_id}_1",
                    "description": "Floral summer dress",
                    "media": {"images": {"orig": {"url": "https://picsum.photos/400/600?random=1"}}},
                },
                {
                    "id": f"pin_{board_id}_2",
                    "description": "Casual white shirt",
                    "media": {"images": {"orig": {"url": "https://picsum.photos/400/600?random=2"}}},
                },
            ]
        pins: list[dict] = []
        cursor = None
        while True:
            params: dict = {"page_size": 25}
            if cursor:
                params["bookmark"] = cursor
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{PinterestService.BASE}/boards/{board_id}/pins",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params=params,
                )
                if not resp.is_success:
                    raise PinterestAPIError(f"Pins fetch failed: {resp.text}")
                data = resp.json()
                pins.extend(data.get("items", []))
                cursor = data.get("bookmark")
                if not cursor:
                    break
        return pins
