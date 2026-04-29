"""Users router: profile, style preferences, GDPR data deletion."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.interaction import ProductRecommendation, UserInteraction
from app.models.pinterest import PinterestBoard, PinterestPin
from app.models.user import User
from app.schemas.user import UserProfile, UserUpdate
from app.services import auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user: User = Depends(auth_service.get_current_user),
) -> UserProfile:
    """Return the full profile (including style preferences) for the authenticated user."""
    return UserProfile.model_validate(current_user)


@router.put("/preferences", response_model=UserProfile)
async def update_preferences(
    body: UserUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    """Update the current user's style preferences and/or email / display name."""
    if body.email is not None:
        current_user.email = body.email
    if body.display_name is not None:
        current_user.display_name = body.display_name
    if body.style_preferences is not None:
        # Merge preferences rather than replace to preserve Pinterest token etc.
        merged = dict(current_user.style_preferences or {})
        merged.update(body.style_preferences)
        current_user.style_preferences = merged

    await db.commit()
    await db.refresh(current_user)
    return UserProfile.model_validate(current_user)


@router.delete("/data", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_data(
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Permanently delete all data for the authenticated user (GDPR right to erasure).

    Cascades to boards, pins, interactions, and recommendations.
    The user record itself is also hard-deleted.
    """
    user_id = current_user.id

    # Cascade deletes should handle child rows but we explicitly clean up
    # in order to be safe even without FK cascade configs.
    await db.execute(delete(ProductRecommendation).where(ProductRecommendation.user_id == user_id))
    await db.execute(delete(UserInteraction).where(UserInteraction.user_id == user_id))

    # Pins are children of boards – delete boards which cascades to pins
    boards_result = await db.execute(
        select(PinterestBoard).where(PinterestBoard.user_id == user_id)
    )
    for board in boards_result.scalars().all():
        await db.execute(delete(PinterestPin).where(PinterestPin.board_id == board.id))
    await db.execute(delete(PinterestBoard).where(PinterestBoard.user_id == user_id))

    await db.delete(current_user)
    await db.commit()
    logger.info("Deleted all data for user %s", user_id)
