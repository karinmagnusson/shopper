"""Celery tasks for product recommendation generation."""

import asyncio
import logging
from uuid import UUID

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a synchronous Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.generate_recommendations")
def generate_recommendations(self, user_id: str) -> dict:
    """Celery task: compute and persist product recommendations for a user.

    This should be called after pin analysis is complete.

    Args:
        user_id: String UUID of the target user.

    Returns:
        Dict with count of recommendations generated.
    """
    async def _generate(user_id_str: str) -> dict:
        from app.database import AsyncSessionLocal
        from app.services.recommendation_service import generate_recommendations_for_user

        async with AsyncSessionLocal() as db:
            recs = await generate_recommendations_for_user(
                user_id=UUID(user_id_str), db=db
            )
            await db.commit()
            return {"recommendations_generated": len(recs), "user_id": user_id_str}

    try:
        return _run_async(_generate(user_id))
    except Exception as exc:
        logger.exception("generate_recommendations failed for user %s", user_id)
        raise self.retry(exc=exc)
