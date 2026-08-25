from aio_pika import DeliveryMode, ExchangeType, Message

from app.application.interfaces.message_broker import MessageBroker
from app.infrastructure.messaging.rabbitmq import RabbitMQConnection


class RabbitMQEventPublisher(MessageBroker):
    """AMQP publisher implementing the MessageBroker port with aio-pika."""

    def __init__(self, connection: RabbitMQConnection) -> None:
        self._connection = connection

    async def publish(self, exchange: str, routing_key: str, payload: bytes) -> None:
        """Declare the durable topic exchange if needed and publish persistently."""
        connection = await self._connection.connect()
        channel = await connection.channel()
        topic_exchange = await channel.declare_exchange(exchange, ExchangeType.TOPIC, durable=True)

        message = Message(
            body=payload,
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
        )
        await topic_exchange.publish(message, routing_key=routing_key)
