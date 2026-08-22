from app.core.config import Settings, get_settings


def test_default_settings() -> None:
    settings = Settings()
    assert settings.APP_NAME == "EcoTrace Engine"
    assert settings.APP_VERSION == "0.1.0"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.PORT == 8000
    assert settings.LOG_FORMAT == "json"


def test_custom_settings(test_settings: Settings) -> None:
    assert test_settings.ENVIRONMENT == "test"
    assert test_settings.POSTGRES_USER == "test_user"
    assert test_settings.REDIS_DB == 15


def test_async_database_url_computed(test_settings: Settings) -> None:
    expected_url = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_ecotrace_db"
    assert test_settings.async_database_url == expected_url


def test_explicit_database_url() -> None:
    custom_url = "postgresql+asyncpg://custom:custom@remote:5433/custom_db"
    settings = Settings(DATABASE_URL=custom_url)
    assert settings.async_database_url == custom_url


def test_redis_connection_url_without_password(test_settings: Settings) -> None:
    assert test_settings.redis_connection_url == "redis://localhost:6379/15"


def test_redis_connection_url_with_password() -> None:
    settings = Settings(REDIS_PASSWORD="secret_redis_pass", REDIS_DB=2)
    assert settings.redis_connection_url == "redis://:secret_redis_pass@localhost:6379/2"


def test_explicit_redis_url() -> None:
    custom_url = "redis://custom-host:6380/3"
    settings = Settings(REDIS_URL=custom_url)
    assert settings.redis_connection_url == custom_url


def test_rabbitmq_connection_url_computed(test_settings: Settings) -> None:
    expected_url = "amqp://test_rabbit:test_rabbit_pass@localhost:5672//"
    assert test_settings.rabbitmq_connection_url == expected_url


def test_explicit_rabbitmq_url() -> None:
    custom_url = "amqp://user:pass@broker:5672/vhost"
    settings = Settings(RABBITMQ_URL=custom_url)
    assert settings.rabbitmq_connection_url == custom_url


def test_celery_defaults(test_settings: Settings) -> None:
    assert test_settings.celery_broker == test_settings.rabbitmq_connection_url
    assert test_settings.celery_backend == "redis://localhost:6379/1"


def test_celery_backend_with_password() -> None:
    settings = Settings(REDIS_PASSWORD="redis_secret")
    assert settings.celery_backend == "redis://:redis_secret@localhost:6379/1"


def test_explicit_celery_urls() -> None:
    broker = "amqp://custom:custom@broker:5672//"
    backend = "redis://custom:6379/5"
    settings = Settings(CELERY_BROKER_URL=broker, CELERY_RESULT_BACKEND=backend)
    assert settings.celery_broker == broker
    assert settings.celery_backend == backend


def test_get_settings_singleton() -> None:
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
