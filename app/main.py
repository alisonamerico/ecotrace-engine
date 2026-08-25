import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.metrics import router as metrics_router
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.telemetry import configure_telemetry
from app.domain.exceptions import DomainException
from app.infrastructure.messaging.publisher import RabbitMQEventPublisher
from app.infrastructure.messaging.rabbitmq import RabbitMQConnection


def _run_alembic_upgrade() -> None:
    """Run Alembic upgrade synchronously (called via asyncio.to_thread)."""
    alembic_cfg = AlembicConfig("migrations/alembic.ini")
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Wire shared infrastructure lazily; close it on shutdown."""
    settings = get_settings()
    configure_logging(log_level=settings.LOG_LEVEL)
    configure_telemetry()
    logger = get_logger()
    logger.info("app_startup", environment=settings.ENVIRONMENT, version=settings.APP_VERSION)

    await asyncio.to_thread(_run_alembic_upgrade)
    logger.info("database_migrated")

    connection = RabbitMQConnection()
    app.state.message_publisher = RabbitMQEventPublisher(connection)
    yield
    await connection.close()
    logger.info("app_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )
    application.include_router(api_router, prefix=settings.API_V1_STR)
    application.include_router(metrics_router)

    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # noqa: PLC0415

        FastAPIInstrumentor.instrument_app(application)
    except Exception:
        pass

    @application.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
        """Map pure-domain validation failures to HTTP 422 responses."""
        del request
        return JSONResponse(status_code=422, content={"detail": exc.message})

    return application


app = create_app()
