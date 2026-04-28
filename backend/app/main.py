"""FastAPI application entry point."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import auth, boards, products, users
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Shopper – Pinterest Fashion Finder",
    description="Discover shoppable fashion inspired by your Pinterest boards.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware required for PKCE code_verifier storage during OAuth flow
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,
    https_only=False,  # Set True in production behind HTTPS
    same_site="lax",
)

# ------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------

app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(products.router)
app.include_router(users.router)

# ------------------------------------------------------------------
# Global error handlers
# ------------------------------------------------------------------


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled error on %s %s: %s", request.method, request.url, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------


@app.get("/health", tags=["meta"])
async def health_check() -> dict:
    """Return service health status."""
    return {"status": "ok", "service": "shopper-backend"}


@app.get("/", tags=["meta"])
async def root() -> dict:
    return {"message": "Shopper API – see /docs for usage"}
