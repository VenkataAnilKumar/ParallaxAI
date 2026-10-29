"""Pytest configuration and shared fixtures."""

import os
import uuid
from collections.abc import AsyncGenerator

# Settings are read at import time, so provide safe defaults before importing app.
os.environ.setdefault(
    "DATABASE_URL", "postgresql://parallax:parallax@localhost:5432/parallax_test"
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-tests-only")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test")
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-service-key")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-jwt-secret")

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from app.config import settings  # noqa: E402
from app.core.auth import get_current_user  # noqa: E402
from app.database import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402
from app.models.user import User  # noqa: E402


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    _engine = create_async_engine(settings.async_database_url, echo=False)
    async with _engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest.fixture
async def db(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Session bound to an outer transaction that is rolled back after each test.

    Commits made by application code become savepoints, so tests stay isolated.
    """
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


@pytest.fixture
async def user(db: AsyncSession) -> User:
    u = User(id=uuid.uuid4(), email=f"{uuid.uuid4().hex}@parallax.app", full_name="Test")
    db.add(u)
    await db.flush()
    return u


@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def auth_client(client: AsyncClient, user: User) -> AsyncClient:
    """Client authenticated as `user` (bypasses Supabase JWT verification)."""
    app.dependency_overrides[get_current_user] = lambda: user
    return client
