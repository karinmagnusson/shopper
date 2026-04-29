"""Pinterest API v5 integration service."""

import asyncio
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.pinterest import PinterestBoard, PinterestPin
from app.models.user import User

logger = logging.getLogger(__name__)

PINTEREST_API_BASE = "https://api.pinterest.com/v5"
PINTEREST_TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"


async def exchange_code_for_token(code: str) -> dict:
    """Exchange an OAuth authorisation code for Pinterest tokens.

    Args:
        code: The authorisation code from Pinterest redirect.

    Returns:
        Token response dict containing access_token, refresh_token etc.

    Raises:
        httpx.HTTPStatusError on non-2xx responses.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            PINTEREST_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.PINTEREST_REDIRECT_URI,
            },
            auth=(settings.PINTEREST_CLIENT_ID, settings.PINTEREST_CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


async def get_pinterest_user(access_token: str) -> dict:
    """Fetch authenticated user profile from Pinterest.

    Args:
        access_token: Pinterest OAuth access token.

    Returns:
        Pinterest user object dict.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PINTEREST_API_BASE}/user_account",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15.0,
        )
        response.raise_for_status()
        return response.json()


async def _request_with_backoff(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    access_token: str,
    params: dict | None = None,
    max_retries: int = 5,
) -> dict:
    """Make an API request with exponential backoff on rate-limit errors (429).

    Args:
        client: Shared httpx async client.
        method: HTTP method string.
        url: Full request URL.
        access_token: Bearer token.
        params: Optional query parameters.
        max_retries: Maximum retry attempts.

    Returns:
        Parsed JSON response dict.
    """
    delay = 1.0
    for attempt in range(max_retries):
        response = await client.request(
            method,
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
            timeout=20.0,
        )
        if response.status_code == 429:
            wait = float(response.headers.get("Retry-After", delay))
            logger.warning("Pinterest rate limit hit, waiting %.1fs (attempt %d)", wait, attempt + 1)
            await asyncio.sleep(wait)
            delay = min(delay * 2, 60.0)
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("Max retries exceeded for Pinterest API request")


async def fetch_user_boards(access_token: str) -> list[dict]:
    """Fetch all boards for the authenticated user, handling pagination.

    Args:
        access_token: Pinterest OAuth access token.

    Returns:
        List of board dicts from Pinterest API.
    """
    boards: list[dict] = []
    bookmark: str | None = None

    async with httpx.AsyncClient() as client:
        while True:
            params: dict = {"page_size": 100}
            if bookmark:
                params["bookmark"] = bookmark

            data = await _request_with_backoff(
                client, "GET", f"{PINTEREST_API_BASE}/boards", access_token, params
            )
            boards.extend(data.get("items", []))
            bookmark = data.get("bookmark")
            if not bookmark:
                break

    return boards


async def fetch_board_pins(access_token: str, pinterest_board_id: str) -> list[dict]:
    """Fetch all pins from a specific board, handling pagination.

    Args:
        access_token: Pinterest OAuth access token.
        pinterest_board_id: The Pinterest board ID string.

    Returns:
        List of pin dicts from Pinterest API.
    """
    pins: list[dict] = []
    bookmark: str | None = None

    async with httpx.AsyncClient() as client:
        while True:
            params: dict = {"page_size": 100}
            if bookmark:
                params["bookmark"] = bookmark

            data = await _request_with_backoff(
                client,
                "GET",
                f"{PINTEREST_API_BASE}/boards/{pinterest_board_id}/pins",
                access_token,
                params,
            )
            pins.extend(data.get("items", []))
            bookmark = data.get("bookmark")
            if not bookmark:
                break

    return pins


async def sync_boards_to_db(user: User, access_token: str, db: AsyncSession) -> list[PinterestBoard]:
    """Fetch boards from Pinterest and upsert them into the database.

    Args:
        user: The User ORM instance.
        access_token: Pinterest OAuth access token.
        db: Async DB session.

    Returns:
        List of upserted PinterestBoard ORM objects.
    """
    remote_boards = await fetch_user_boards(access_token)
    saved: list[PinterestBoard] = []

    for board_data in remote_boards:
        stmt = select(PinterestBoard).where(
            PinterestBoard.pinterest_board_id == board_data["id"]
        )
        result = await db.execute(stmt)
        board: PinterestBoard | None = result.scalar_one_or_none()

        media = board_data.get("media") or {}
        cover_images = media.get("image_cover_url") or board_data.get("cover_image_url")

        if board is None:
            board = PinterestBoard(
                user_id=user.id,
                pinterest_board_id=board_data["id"],
                name=board_data.get("name", ""),
                description=board_data.get("description"),
                cover_image_url=cover_images,
                pin_count=board_data.get("pin_count", 0),
                follower_count=board_data.get("follower_count", 0),
                board_metadata=board_data,
                synced_at=datetime.now(timezone.utc),
            )
            db.add(board)
        else:
            board.name = board_data.get("name", board.name)
            board.description = board_data.get("description", board.description)
            board.cover_image_url = cover_images or board.cover_image_url
            board.pin_count = board_data.get("pin_count", board.pin_count)
            board.follower_count = board_data.get("follower_count", board.follower_count)
            board.board_metadata = board_data
            board.synced_at = datetime.now(timezone.utc)

        saved.append(board)

    user.last_sync = datetime.now(timezone.utc)
    await db.flush()
    return saved


async def sync_pins_to_db(
    board: PinterestBoard, access_token: str, db: AsyncSession
) -> list[PinterestPin]:
    """Fetch pins for a board and upsert them into the database.

    Args:
        board: The PinterestBoard ORM instance.
        access_token: Pinterest OAuth access token.
        db: Async DB session.

    Returns:
        List of upserted PinterestPin ORM objects.
    """
    remote_pins = await fetch_board_pins(access_token, board.pinterest_board_id)
    saved: list[PinterestPin] = []

    for pin_data in remote_pins:
        stmt = select(PinterestPin).where(
            PinterestPin.pinterest_pin_id == pin_data["id"]
        )
        result = await db.execute(stmt)
        pin: PinterestPin | None = result.scalar_one_or_none()

        media = pin_data.get("media") or {}
        images = media.get("images") or {}
        orig = images.get("original") or {}
        image_url = orig.get("url") or pin_data.get("image_url", "")

        if pin is None:
            pin = PinterestPin(
                board_id=board.id,
                pinterest_pin_id=pin_data["id"],
                title=pin_data.get("title"),
                description=pin_data.get("description"),
                image_url=image_url,
                link=pin_data.get("link"),
            )
            db.add(pin)
        else:
            pin.title = pin_data.get("title", pin.title)
            pin.description = pin_data.get("description", pin.description)
            pin.image_url = image_url or pin.image_url
            pin.link = pin_data.get("link", pin.link)

        saved.append(pin)

    await db.flush()
    return saved
