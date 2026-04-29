"""Pinterest boards/pins router."""

import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.pinterest import PinterestBoard, PinterestPin
from app.models.user import User
from app.schemas.pinterest import AnalyzeRequest, BoardResponse, PinResponse, SyncRequest
from app.services import auth_service, pinterest_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pinterest", tags=["pinterest"])

# Pinterest access tokens are stored in user.style_preferences["pinterest_token"]
# in the MVP. A production system would use a dedicated token store.
_TOKEN_KEY = "pinterest_access_token"


def _get_access_token(user: User) -> str:
    """Extract stored Pinterest access token from user preferences.

    Raises:
        HTTPException 400 if token is not stored.
    """
    token: str | None = (user.style_preferences or {}).get(_TOKEN_KEY)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pinterest access token not available. Please reconnect your account.",
        )
    return token


@router.get("/boards", response_model=list[BoardResponse])
async def list_boards(
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BoardResponse]:
    """Return cached Pinterest boards for the authenticated user."""
    result = await db.execute(
        select(PinterestBoard)
        .where(PinterestBoard.user_id == current_user.id)
        .order_by(PinterestBoard.name)
    )
    boards = result.scalars().all()
    return [BoardResponse.model_validate(b) for b in boards]


async def _do_board_sync(user_id: UUID, access_token: str) -> None:
    """Background task: sync boards and pins from Pinterest API."""
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            return
        try:
            await pinterest_service.sync_boards_to_db(user, access_token, db)
            await db.commit()
        except Exception:
            logger.exception("Board sync failed for user %s", user_id)
            await db.rollback()


@router.post("/boards/sync", status_code=status.HTTP_202_ACCEPTED)
async def sync_boards(
    body: SyncRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(auth_service.get_current_user),
) -> dict:
    """Trigger an asynchronous Pinterest board sync for the current user."""
    access_token = _get_access_token(current_user)
    background_tasks.add_task(_do_board_sync, current_user.id, access_token)
    return {"message": "Board sync started", "user_id": str(current_user.id)}


@router.get("/pins/{board_id}", response_model=list[PinResponse])
async def list_pins(
    board_id: UUID,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PinResponse]:
    """Return cached pins for the given board (owned by the current user)."""
    board_result = await db.execute(
        select(PinterestBoard).where(
            PinterestBoard.id == board_id,
            PinterestBoard.user_id == current_user.id,
        )
    )
    board = board_result.scalar_one_or_none()
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")

    pins_result = await db.execute(
        select(PinterestPin).where(PinterestPin.board_id == board_id)
    )
    pins = pins_result.scalars().all()
    return [PinResponse.model_validate(p) for p in pins]


async def _do_analyze_pins(pin_ids: list[str]) -> None:
    """Background task: run fashion analysis on a list of pin IDs."""
    from app.database import AsyncSessionLocal
    from app.services.fashion_analysis import analyze_pin_image
    from datetime import datetime

    async with AsyncSessionLocal() as db:
        for pin_id_str in pin_ids:
            try:
                result = await db.execute(
                    select(PinterestPin).where(PinterestPin.pinterest_pin_id == pin_id_str)
                )
                pin = result.scalar_one_or_none()
                if pin is None:
                    # Try by UUID
                    result2 = await db.execute(
                        select(PinterestPin).where(PinterestPin.id == pin_id_str)
                    )
                    pin = result2.scalar_one_or_none()

                if pin and pin.image_url:
                    analysis = await analyze_pin_image(pin.image_url)
                    pin.analysis_data = analysis.to_dict()
                    pin.analyzed_at = datetime.utcnow()
                    await db.commit()
            except Exception:
                logger.exception("Failed to analyse pin %s", pin_id_str)
                await db.rollback()


@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_pins(
    body: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(auth_service.get_current_user),
) -> dict:
    """Trigger fashion analysis on selected pin IDs (background task)."""
    if not body.pin_ids:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No pin IDs provided")

    background_tasks.add_task(_do_analyze_pins, body.pin_ids)
    return {"message": "Analysis started", "pin_count": len(body.pin_ids)}
