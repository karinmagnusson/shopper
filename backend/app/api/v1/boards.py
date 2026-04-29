import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.cache import cache_get, cache_set
from app.models.user import User
from app.models.pinterest import PinterestBoard, PinterestPin
from app.schemas.pinterest import BoardRead, PinRead
from app.services.pinterest import PinterestService, PinterestAPIError
from app.services.image_analysis import ImageAnalysisService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/boards", tags=["boards"])


@router.get("", response_model=list[BoardRead])
async def list_boards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return boards already synced for the authenticated user."""
    boards = (
        db.query(PinterestBoard)
        .filter(PinterestBoard.user_id == current_user.id)
        .all()
    )
    return boards


@router.post("/sync")
async def sync_boards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch all boards from Pinterest and upsert them in the database."""
    if not current_user.access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No Pinterest token")

    try:
        remote_boards = await PinterestService.get_user_boards(current_user.access_token)
    except PinterestAPIError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    synced = 0
    for rb in remote_boards:
        board = (
            db.query(PinterestBoard)
            .filter(
                PinterestBoard.user_id == current_user.id,
                PinterestBoard.pinterest_board_id == rb["id"],
            )
            .first()
        )
        if board is None:
            board = PinterestBoard(
                user_id=current_user.id,
                pinterest_board_id=rb["id"],
                name=rb.get("name", ""),
                description=rb.get("description"),
                cover_image_url=rb.get("media", {}).get("image_cover_url"),
                pin_count=rb.get("pin_count", 0),
                last_synced=datetime.now(timezone.utc),
            )
            db.add(board)
        else:
            board.name = rb.get("name", board.name)
            board.pin_count = rb.get("pin_count", board.pin_count)
            board.last_synced = datetime.now(timezone.utc)
        synced += 1

    db.commit()
    return {"synced": synced}


@router.get("/{board_id}/pins", response_model=list[PinRead])
async def list_pins(
    board_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    board = (
        db.query(PinterestBoard)
        .filter(
            PinterestBoard.pinterest_board_id == board_id,
            PinterestBoard.user_id == current_user.id,
        )
        .first()
    )
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")

    return db.query(PinterestPin).filter(PinterestPin.board_id == board.id).all()


@router.post("/{board_id}/sync-pins")
async def sync_pins(
    board_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch pins for a board from Pinterest and run AI analysis."""
    if not current_user.access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No Pinterest token")

    board = (
        db.query(PinterestBoard)
        .filter(
            PinterestBoard.pinterest_board_id == board_id,
            PinterestBoard.user_id == current_user.id,
        )
        .first()
    )
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")

    try:
        remote_pins = await PinterestService.get_board_pins(
            current_user.access_token, board_id
        )
    except PinterestAPIError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    synced = 0
    for rp in remote_pins:
        pin = (
            db.query(PinterestPin)
            .filter(PinterestPin.pinterest_pin_id == rp["id"])
            .first()
        )
        image_url = (rp.get("media", {}) or {}).get("images", {}).get("orig", {}).get("url")
        if pin is None:
            pin = PinterestPin(
                board_id=board.id,
                pinterest_pin_id=rp["id"],
                image_url=image_url,
                description=rp.get("description") or rp.get("note"),
                link=rp.get("link"),
            )
            db.add(pin)
        else:
            pin.image_url = image_url or pin.image_url

        # Run analysis
        if image_url and not pin.analysis_data:
            analysis = await ImageAnalysisService.analyze_image(image_url)
            pin.analysis_data = analysis
            pin.analyzed_at = datetime.now(timezone.utc)

        synced += 1

    board.last_synced = datetime.now(timezone.utc)
    db.commit()
    return {"synced": synced}
