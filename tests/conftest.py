from collections.abc import Generator

import pytest

from app.core.config import Settings, get_settings


@pytest.fixture
def test_settings() -> Settings:
    """Fixture providing isolated test settings."""
    return Settings(
        _env_file=None,
        ENVIRONMENT="test",
        DEBUG=True,
        POSTGRES_SERVER="localhost",
        POSTGRES_PORT=5432,
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="test_password",
        POSTGRES_DB="test_ecotrace_db",
        DATABASE_URL=None,
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        REDIS_DB=15,
        REDIS_PASSWORD=None,
        REDIS_URL=None,
        RABBITMQ_HOST="localhost",
        RABBITMQ_PORT=5672,
        RABBITMQ_USER="test_rabbit",
        RABBITMQ_PASSWORD="test_rabbit_pass",
        RABBITMQ_URL=None,
        CELERY_BROKER_URL=None,
        CELERY_RESULT_BACKEND=None,
    )


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Generator[None]:
    """Ensure lru_cache for get_settings is cleared between tests."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
