"""Celery tasks for Pinterest board/pin synchronisation and analysis."""

import asyncio
import logging
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a synchronous Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30, name="tasks.sync_pinterest_boards")
def sync_pinterest_boards(self, user_id: str) -> dict:
    """Celery task: fetch and cache a user's Pinterest boards.

    Args:
        user_id: String UUID of the target user.

    Returns:
        Dict with counts of synced boards.
    """
    async def _sync(user_id_str: str) -> dict:
        from sqlalchemy import select
        from app.database import AsyncSessionLocal
        from app.models.user import User
        from app.services.pinterest_service import sync_boards_to_db

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == user_id_str))
            user = result.scalar_one_or_none()
            if user is None:
                return {"error": "User not found", "user_id": user_id_str}

            access_token: str = (user.style_preferences or {}).get("pinterest_access_token", "")
            if not access_token:
                return {"error": "No Pinterest token stored", "user_id": user_id_str}

            boards = await sync_boards_to_db(user, access_token, db)
            await db.commit()
            return {"boards_synced": len(boards), "user_id": user_id_str}

    try:
        return _run_async(_sync(user_id))
    except Exception as exc:
        logger.exception("sync_pinterest_boards failed for user %s", user_id)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.analyze_pin")
def analyze_pin(self, pin_id: str) -> dict:
    """Celery task: run fashion analysis on a single pin.

    Args:
        pin_id: String UUID or Pinterest pin ID of the target pin.

    Returns:
        Dict with analysis summary or error.
    """
    async def _analyze(pin_id_str: str) -> dict:
        from sqlalchemy import select
        from app.database import AsyncSessionLocal
        from app.models.pinterest import PinterestPin
        from app.services.fashion_analysis import analyze_pin_image

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(PinterestPin).where(PinterestPin.pinterest_pin_id == pin_id_str)
            )
            pin = result.scalar_one_or_none()
            if pin is None:
                return {"error": "Pin not found", "pin_id": pin_id_str}

            if not pin.image_url:
                return {"error": "Pin has no image URL", "pin_id": pin_id_str}

            analysis = await analyze_pin_image(pin.image_url)
            pin.analysis_data = analysis.to_dict()
            pin.analyzed_at = datetime.now(timezone.utc)
            await db.commit()
            return {
                "pin_id": pin_id_str,
                "categories": analysis.categories,
                "dominant_style": analysis.dominant_style,
            }

    try:
        return _run_async(_analyze(pin_id))
    except Exception as exc:
        logger.exception("analyze_pin failed for pin %s", pin_id)
        raise self.retry(exc=exc)
