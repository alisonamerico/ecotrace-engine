from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.infrastructure.messaging.publisher import RabbitMQEventPublisher
from app.infrastructure.messaging.rabbitmq import RabbitMQConnection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Wire shared infrastructure lazily; close it on shutdown."""
    connection = RabbitMQConnection()
    app.state.message_publisher = RabbitMQEventPublisher(connection)
    yield
    await connection.close()


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )
    application.include_router(api_router, prefix=settings.API_V1_STR)
    return application


app = create_app()
