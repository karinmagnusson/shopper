"""Tests for product endpoints."""

from decimal import Decimal
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models.product import Product
from app.models.user import User
from app.services.auth_service import create_access_token

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
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
async def auth_context(db_session: AsyncSession):
    """Returns (user, auth_headers) with a live DB session."""
    user = User(id=uuid4(), pinterest_id="prod_test_user")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = create_access_token(str(user.id))
    return user, {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def seeded_products(db_session: AsyncSession):
    p1 = Product(
        id=uuid4(), title="Blue Floral Dress", affiliate_url="https://example.com/dress1",
        category="dresses", brand="StyleCo", price=Decimal("49.99"),
        colors=["#0000ff", "#ffffff"], sizes=["S", "M", "L"], style_tags=["casual", "bohemian"],
    )
    p2 = Product(
        id=uuid4(), title="Black Denim Jacket", affiliate_url="https://example.com/jacket1",
        category="outerwear", brand="DenimHub", price=Decimal("89.99"),
        colors=["#000000"], sizes=["M", "L", "XL"], style_tags=["casual", "streetwear"],
    )
    db_session.add_all([p1, p2])
    await db_session.commit()
    return p1, p2


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


# ── GET /products/search ──────────────────────────────────────────────────────

async def test_search_unauthenticated(async_client: AsyncClient):
    response = await async_client.get("/products/search")
    assert response.status_code == 401


async def test_search_returns_all(async_client: AsyncClient, auth_context, seeded_products):
    _, headers = auth_context
    response = await async_client.get("/products/search", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_search_by_category(async_client: AsyncClient, auth_context, seeded_products):
    _, headers = auth_context
    response = await async_client.get("/products/search?category=dresses", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "dresses"


async def test_search_by_brand(async_client: AsyncClient, auth_context, seeded_products):
    _, headers = auth_context
    response = await async_client.get("/products/search?brand=DenimHub", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["brand"] == "DenimHub"


async def test_search_price_filter(async_client: AsyncClient, auth_context, seeded_products):
    _, headers = auth_context
    response = await async_client.get("/products/search?max_price=60", headers=headers)
    assert response.status_code == 200
    results = response.json()
    assert all(float(p["price"]) <= 60 for p in results)


# ── GET /products/{id} ────────────────────────────────────────────────────────

async def test_get_product_not_found(async_client: AsyncClient, auth_context):
    _, headers = auth_context
    response = await async_client.get(f"/products/{uuid4()}", headers=headers)
    assert response.status_code == 404


async def test_get_product_found(async_client: AsyncClient, auth_context, seeded_products):
    _, headers = auth_context
    p1, _ = seeded_products
    response = await async_client.get(f"/products/{p1.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Blue Floral Dress"


# ── POST /products/track-click ────────────────────────────────────────────────

async def test_track_click_not_found(async_client: AsyncClient, auth_context):
    _, headers = auth_context
    response = await async_client.post(f"/products/track-click?product_id={uuid4()}", headers=headers)
    assert response.status_code == 404


async def test_track_click_success(async_client: AsyncClient, auth_context, seeded_products):
    _, headers = auth_context
    _, p2 = seeded_products
    response = await async_client.post(f"/products/track-click?product_id={p2.id}", headers=headers)
    assert response.status_code == 204


# ── GET /products/recommendations ────────────────────────────────────────────

async def test_recommendations_empty(async_client: AsyncClient, auth_context):
    _, headers = auth_context
    response = await async_client.get("/products/recommendations", headers=headers)
    assert response.status_code == 200
    assert response.json() == []
