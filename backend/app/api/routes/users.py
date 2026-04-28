"""User profile and preferences endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import delete

from app.api.deps import CurrentUser, DBSession
from app.models.interaction import UserInteraction
from app.models.pinterest import PinterestBoard, PinterestPin
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


class StylePreferences(BaseModel):
    preferred_styles: list[str] = []
    preferred_colors: list[str] = []
    preferred_categories: list[str] = []
    preferred_brands: list[str] = []
    price_range_min: float | None = None
    price_range_max: float | None = None
    size: str | None = None


@router.get("/me")
async def get_current_user_profile(current_user: CurrentUser) -> dict:
    """Return the authenticated user's profile."""
    return {
        "id": str(current_user.id),
        "pinterest_id": current_user.pinterest_id,
        "email": current_user.email,
        "style_preferences": current_user.style_preferences or {},
        "created_at": current_user.created_at.isoformat(),
        "last_sync": current_user.last_sync.isoformat() if current_user.last_sync else None,
    }


@router.put("/me/preferences")
async def update_preferences(
    preferences: StylePreferences,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Update the user's style preferences."""
    current_user.style_preferences = preferences.model_dump(exclude_none=True)
    await db.commit()
    await db.refresh(current_user)
    return {
        "message": "Preferences updated",
        "style_preferences": current_user.style_preferences,
    }


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(current_user: CurrentUser, db: DBSession) -> None:
    """
    Permanently delete the user account and all associated data.

    Cascading deletes handle boards, pins, and interactions via FK constraints.
    """
    user_id = current_user.id

    # Explicitly delete interactions (not covered by cascade from User)
    await db.execute(delete(UserInteraction).where(UserInteraction.user_id == user_id))

    await db.delete(current_user)
    await db.commit()
    logger.info("User %s deleted their account", user_id)
