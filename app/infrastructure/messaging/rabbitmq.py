import aio_pika

from app.core.config import get_settings


class RabbitMQConnection:
    """Lazy, reconnect-safe holder for a robust AMQP connection."""

    def __init__(self, url: str | None = None) -> None:
        self._url = url or get_settings().rabbitmq_connection_url
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None

    async def connect(self) -> aio_pika.abc.AbstractRobustConnection:
        """Return the live robust connection, establishing it on first use."""
        if self._connection is None or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(self._url)
        return self._connection

    async def close(self) -> None:
        """Close the underlying connection if open."""
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None
