"""Pinterest board and pin management endpoints."""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.core.security import decrypt_token
from app.models.pinterest import PinterestBoard, PinterestPin
from app.services.image_analysis import image_analysis_service
from app.services.pinterest_service import pinterest_service
from app.utils.cache import cache_delete_pattern

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/boards", tags=["boards"])


@router.get("")
async def list_boards(current_user: CurrentUser, db: DBSession) -> dict:
    """Return all Pinterest boards belonging to the authenticated user."""
    result = await db.execute(
        select(PinterestBoard)
        .where(PinterestBoard.user_id == current_user.id)
        .order_by(PinterestBoard.name)
    )
    boards = result.scalars().all()

    return {
        "boards": [
            {
                "id": str(b.id),
                "pinterest_board_id": b.pinterest_board_id,
                "name": b.name,
                "description": b.description,
                "cover_image_url": b.cover_image_url,
                "pin_count": b.pin_count,
                "last_synced": b.last_synced.isoformat() if b.last_synced else None,
            }
            for b in boards
        ],
        "total": len(boards),
    }


@router.post("/sync")
async def sync_boards(current_user: CurrentUser, db: DBSession) -> dict:
    """Fetch boards from Pinterest API and upsert them in the database."""
    access_token = decrypt_token(current_user.access_token_encrypted)

    try:
        raw_boards = await pinterest_service.get_boards(
            str(current_user.id), access_token
        )
    except Exception as exc:
        logger.error("Board sync failed for user %s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch boards from Pinterest",
        ) from exc

    synced = 0
    for raw in raw_boards:
        pin_board_id: str = raw.get("id", "")
        result = await db.execute(
            select(PinterestBoard).where(
                PinterestBoard.pinterest_board_id == pin_board_id
            )
        )
        board = result.scalar_one_or_none()

        media = raw.get("media", {})
        cover_url: str | None = None
        if isinstance(media, dict):
            images = media.get("image_cover_url") or media.get("pin_thumbnail_urls", [None])
            cover_url = images[0] if isinstance(images, list) else images

        if board is None:
            board = PinterestBoard(
                id=uuid.uuid4(),
                user_id=current_user.id,
                pinterest_board_id=pin_board_id,
                name=raw.get("name", ""),
                description=raw.get("description"),
                cover_image_url=cover_url,
                pin_count=raw.get("pin_count", 0),
                last_synced=datetime.now(timezone.utc),
            )
            db.add(board)
        else:
            board.name = raw.get("name", board.name)
            board.description = raw.get("description", board.description)
            board.cover_image_url = cover_url or board.cover_image_url
            board.pin_count = raw.get("pin_count", board.pin_count)
            board.last_synced = datetime.now(timezone.utc)

        synced += 1

    await db.commit()

    # Invalidate board cache
    await cache_delete_pattern(f"boards:{current_user.id}")

    return {"synced": synced, "message": f"Synced {synced} boards"}


@router.get("/{board_id}/pins")
async def list_pins(
    board_id: str = Path(...),
    current_user: CurrentUser = None,
    db: DBSession = None,
) -> dict:
    """Return all stored pins for a given board."""
    result = await db.execute(
        select(PinterestBoard).where(
            PinterestBoard.pinterest_board_id == board_id,
            PinterestBoard.user_id == current_user.id,
        )
    )
    board = result.scalar_one_or_none()
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")

    pins_result = await db.execute(
        select(PinterestPin).where(PinterestPin.board_id == board.id)
    )
    pins = pins_result.scalars().all()

    return {
        "pins": [
            {
                "id": str(p.id),
                "pinterest_pin_id": p.pinterest_pin_id,
                "image_url": p.image_url,
                "description": p.description,
                "link": p.link,
                "analyzed_at": p.analyzed_at.isoformat() if p.analyzed_at else None,
                "analysis_data": p.analysis_data,
            }
            for p in pins
        ],
        "total": len(pins),
    }


@router.get("/{board_id}/analyze")
async def analyze_board(
    board_id: str = Path(...),
    current_user: CurrentUser = None,
    db: DBSession = None,
) -> dict:
    """
    Fetch pins from Pinterest for a board, persist them, and analyse their images.
    """
    result = await db.execute(
        select(PinterestBoard).where(
            PinterestBoard.pinterest_board_id == board_id,
            PinterestBoard.user_id == current_user.id,
        )
    )
    board = result.scalar_one_or_none()
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")

    access_token = decrypt_token(current_user.access_token_encrypted)

    try:
        raw_pins = await pinterest_service.get_board_pins(
            str(current_user.id), board_id, access_token
        )
    except Exception as exc:
        logger.error("Pin fetch failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch pins from Pinterest",
        ) from exc

    analyses: list[dict] = []
    for raw in raw_pins[:50]:  # Limit to first 50 to stay within API quotas
        pin_id: str = raw.get("id", "")
        media = raw.get("media", {})
        images = media.get("images", {})
        image_url: str | None = (
            images.get("orig", {}).get("url")
            or images.get("736x", {}).get("url")
        )

        # Upsert pin record
        pin_result = await db.execute(
            select(PinterestPin).where(PinterestPin.pinterest_pin_id == pin_id)
        )
        pin = pin_result.scalar_one_or_none()
        if pin is None:
            pin = PinterestPin(
                id=uuid.uuid4(),
                board_id=board.id,
                pinterest_pin_id=pin_id,
                image_url=image_url,
                description=raw.get("description"),
                link=raw.get("link"),
            )
            db.add(pin)
        else:
            pin.image_url = image_url or pin.image_url

        # Analyse image
        if image_url and not pin.analysis_data:
            try:
                analysis = await image_analysis_service.analyze_image(image_url)
                pin.analysis_data = analysis
                pin.analyzed_at = datetime.now(timezone.utc)
                analyses.append(analysis)
            except Exception as exc:
                logger.warning("Image analysis failed for pin %s: %s", pin_id, exc)

    await db.commit()

    return {
        "board_id": board_id,
        "pins_processed": len(raw_pins[:50]),
        "pins_analyzed": len(analyses),
        "analyses": analyses,
    }
