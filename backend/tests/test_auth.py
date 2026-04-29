"""Tests for authentication endpoints."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.services.auth_service import create_access_token

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    """In-memory SQLite session per test."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    """HTTPX async client with DB override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_user(db_session: AsyncSession):
    """Persisted user + JWT token."""
    user = User(id=uuid4(), pinterest_id="test_pinterest_123", display_name="Test User", email="test@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = create_access_token(str(user.id))
    return user, token


# ── Health check ──────────────────────────────────────────────────────────────

async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ── GET /auth/me ──────────────────────────────────────────────────────────────

async def test_get_me_unauthenticated(async_client: AsyncClient):
    response = await async_client.get("/auth/me")
    assert response.status_code == 401


async def test_get_me_invalid_token(async_client: AsyncClient):
    response = await async_client.get("/auth/me", headers={"Authorization": "Bearer invalid.token"})
    assert response.status_code == 401


async def test_get_me_authenticated(async_client: AsyncClient, sample_user):
    user, token = sample_user
    response = await async_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["pinterest_id"] == "test_pinterest_123"
    assert data["display_name"] == "Test User"


# ── POST /auth/pinterest/oauth ────────────────────────────────────────────────

async def test_pinterest_oauth_bad_code(async_client: AsyncClient):
    with patch("app.routers.auth.pinterest_service.exchange_code_for_token", side_effect=Exception("bad code")):
        response = await async_client.post("/auth/pinterest/oauth", json={"code": "bad_code"})
    assert response.status_code == 502


async def test_pinterest_oauth_success(async_client: AsyncClient):
    mock_token = {"access_token": "mock_pinterest_token"}
    mock_profile = {"id": "pin_user_999", "username": "fashionista", "email": "fashion@example.com", "profile_image": {}}
    with (
        patch("app.routers.auth.pinterest_service.exchange_code_for_token", new_callable=AsyncMock, return_value=mock_token),
        patch("app.routers.auth.pinterest_service.get_pinterest_user", new_callable=AsyncMock, return_value=mock_profile),
    ):
        response = await async_client.post("/auth/pinterest/oauth", json={"code": "valid_code", "state": "xyz"})
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["display_name"] == "fashionista"


# ── POST /auth/logout ─────────────────────────────────────────────────────────

async def test_logout(async_client: AsyncClient, sample_user):
    _, token = sample_user
    response = await async_client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204
