from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


@lru_cache
def get_async_engine() -> AsyncEngine:
    """Create and cache the SQLAlchemy async engine."""
    settings = get_settings()
    return create_async_engine(
        settings.async_database_url,
        echo=settings.DEBUG and settings.ENVIRONMENT == "development",
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


@lru_cache
def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create and cache the async sessionmaker factory."""
    engine = get_async_engine()
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Dependency / generator for acquiring an isolated AsyncSession."""
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
