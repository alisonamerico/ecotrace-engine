from functools import lru_cache
from typing import Literal, Self

from decouple import config as decouple_config
from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

config = decouple_config


def _credential(name: str) -> SecretStr:
    """Read a credential through decouple without hardcoding it in source."""
    return SecretStr(str(config(name, default="")))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = True
    APP_NAME: str = "EcoTrace Engine"
    APP_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8081

    # PostgreSQL Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = Field(default_factory=lambda: str(config("POSTGRES_USER", default="")))
    POSTGRES_PASSWORD: SecretStr = Field(default_factory=lambda: _credential("POSTGRES_PASSWORD"))
    POSTGRES_DB: str = "ecotrace_db"
    DATABASE_URL: str | None = None

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD.get_secret_value()}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis (Cache & Distributed Lock)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: SecretStr | None = Field(
        default_factory=lambda: (
            _credential("REDIS_PASSWORD") if config("REDIS_PASSWORD", default="") else None
        )
    )
    REDIS_URL: str | None = None

    @property
    def redis_connection_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        if self.REDIS_PASSWORD is not None:
            return (
                f"redis://:{self.REDIS_PASSWORD.get_secret_value()}"
                f"@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
            )
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # RabbitMQ Broker
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = Field(default_factory=lambda: str(config("RABBITMQ_USER", default="")))
    RABBITMQ_PASSWORD: SecretStr = Field(default_factory=lambda: _credential("RABBITMQ_PASSWORD"))
    RABBITMQ_URL: str | None = None

    @property
    def rabbitmq_connection_url(self) -> str:
        if self.RABBITMQ_URL:
            return self.RABBITMQ_URL
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD.get_secret_value()}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"
        )

    # Celery
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    @property
    def celery_broker(self) -> str:
        if self.CELERY_BROKER_URL:
            return self.CELERY_BROKER_URL
        return self.rabbitmq_connection_url

    @property
    def celery_backend(self) -> str:
        if self.CELERY_RESULT_BACKEND:
            return self.CELERY_RESULT_BACKEND
        if self.REDIS_PASSWORD is not None:
            return f"redis://:{self.REDIS_PASSWORD.get_secret_value()}@{self.REDIS_HOST}:{self.REDIS_PORT}/1"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"

    @model_validator(mode="after")
    def validate_credentials_in_deployed_environments(self) -> Self:
        """Refuse to boot staging/production with missing credentials."""
        if self.ENVIRONMENT in ("staging", "production"):
            missing = [
                name
                for name, value in (
                    ("POSTGRES_USER", self.POSTGRES_USER),
                    ("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD.get_secret_value()),
                    ("RABBITMQ_USER", self.RABBITMQ_USER),
                    ("RABBITMQ_PASSWORD", self.RABBITMQ_PASSWORD.get_secret_value()),
                )
                if not value
            ]
            if missing:
                raise ValueError(f"Missing required credentials for {self.ENVIRONMENT}: {missing}")
        return self

    # SEFAZ Integration
    SEFAZ_MOCK_ENABLED: bool = True
    SEFAZ_TIMEOUT_SECONDS: float = 5.0
    SEFAZ_MAX_RETRIES: int = 3
    SEFAZ_CIRCUIT_BREAKER_FAIL_MAX: int = 5
    SEFAZ_CIRCUIT_BREAKER_RESET_TIMEOUT: int = 30

    # Observability
    OTEL_SERVICE_NAME: str = "ecotrace-engine"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    PROMETHEUS_METRICS_PORT: int = 9090
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
