import asyncio
import json

import aio_pika
import pytest
from testcontainers.community.rabbitmq import RabbitMqContainer

from app.application.use_cases.ingest_invoice import (
    NFE_EXCHANGE,
    NFE_RECEIVED_ROUTING_KEY,
)
from app.infrastructure.messaging.publisher import RabbitMQEventPublisher
from app.infrastructure.messaging.rabbitmq import RabbitMQConnection

pytestmark = pytest.mark.integration


def _amqp_url(rabbit: RabbitMqContainer) -> str:
    params = rabbit.get_connection_params()
    return (
        f"amqp://{rabbit.username}:{rabbit.password}"
        f"@{params.host}:{params.port}{params.virtual_host}"
    )


def test_publishes_persistent_message_to_topic_exchange() -> None:
    with RabbitMqContainer("rabbitmq:3.13-management") as rabbit:
        url = _amqp_url(rabbit)
        connection = RabbitMQConnection(url)
        publisher = RabbitMQEventPublisher(connection)

        payload = b'{"tracking_id": "abc-123"}'

        async def scenario() -> tuple[bytes, str | None, str | None, dict]:
            broker_connection = await aio_pika.connect_robust(url)
            try:
                channel = await broker_connection.channel()
                exchange = await channel.declare_exchange(
                    NFE_EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True
                )
                queue = await channel.declare_queue("publisher-test-queue", exclusive=True)
                await queue.bind(exchange, routing_key=NFE_RECEIVED_ROUTING_KEY)

                await publisher.publish(NFE_EXCHANGE, NFE_RECEIVED_ROUTING_KEY, payload)

                message = await queue.get(timeout=10, fail=False)
                assert message is not None, "no message arrived at the queue"
                delivery_mode = (
                    message.delivery_mode.value
                    if hasattr(message.delivery_mode, "value")
                    else message.delivery_mode
                )
                return (
                    message.body,
                    str(delivery_mode),
                    message.content_type,
                    dict(message.headers or {}),
                )
            finally:
                await broker_connection.close()

        body, delivery_mode, content_type, headers = asyncio.run(scenario())
        parsed = json.loads(body.decode("utf-8"))
        assert parsed[0] == [{"tracking_id": "abc-123"}]
        assert delivery_mode == "2"
        assert content_type == "application/json"
        assert headers.get("task") == "app.workers.tasks.audit_tasks.process_invoice_event"

        asyncio.run(connection.close())
