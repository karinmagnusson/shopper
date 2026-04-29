"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import auth, pinterest, products, users

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown."""
    logger.info("Starting Shopper backend (env=%s)", settings.APP_ENV)
    from app.database import engine
    try:
        async with engine.begin():
            pass
        logger.info("Database connection pool ready")
    except Exception as exc:
        logger.warning("Database warmup skipped: %s", exc)
    yield
    logger.info("Shutting down Shopper backend")
    from app.database import engine as _engine
    await _engine.dispose()


app = FastAPI(
    title="Shopper – Pinterest Fashion Finder API",
    description=(
        "Backend API for the Shopper Pinterest Fashion Finder MVP. "
        "Authenticates with Pinterest OAuth, analyses saved pins using "
        "Google Vision, and returns personalised affiliate product recommendations."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Rate limiting (requires Redis; degrades gracefully when Redis is absent)
# ---------------------------------------------------------------------------
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(pinterest.router)
app.include_router(products.router)
app.include_router(users.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["health"], summary="Health check")
async def health_check() -> JSONResponse:
    """Return 200 when the service is running.

    Used by load balancers and container orchestration health probes.
    """
    return JSONResponse({"status": "ok", "version": app.version})
