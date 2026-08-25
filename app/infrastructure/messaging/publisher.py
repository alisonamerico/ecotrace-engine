import json
import uuid
from typing import Any

from aio_pika import DeliveryMode, ExchangeType, Message

from app.application.interfaces.message_broker import MessageBroker
from app.infrastructure.messaging.rabbitmq import RabbitMQConnection

TASK_CONTENT_TYPE = "application/json"
TASK_CONTENT_ENCODING = "utf-8"
DEFAULT_TASK_NAME = "app.workers.tasks.audit_tasks.process_invoice_event"


class RabbitMQEventPublisher(MessageBroker):
    """AMQP publisher implementing the MessageBroker port with aio-pika."""

    def __init__(self, connection: RabbitMQConnection) -> None:
        self._connection = connection

    async def publish(self, exchange: str, routing_key: str, payload: bytes) -> None:
        """Publish a Celery-compatible message to the given topic exchange."""
        connection = await self._connection.connect()
        channel = await connection.channel()
        topic_exchange = await channel.declare_exchange(exchange, ExchangeType.TOPIC, durable=True)

        task_id = str(uuid.uuid4())

        event_dict = json.loads(payload.decode("utf-8")) if isinstance(payload, bytes) else payload
        body = json.dumps(
            [[event_dict], {}, {"callbacks": None, "errbacks": None, "chain": None, "chord": None}]
        )

        headers: dict[str, Any] = {
            "lang": "py",
            "task": DEFAULT_TASK_NAME,
            "id": task_id,
            "shadow": None,
            "eta": None,
            "expires": None,
            "group": None,
            "group_index": None,
            "retries": 0,
            "timelimit": [None, None],
            "root_id": task_id,
            "parent_id": None,
            "argsrepr": "(event,)",
            "kwargsrepr": "{}",
            "origin": "gen/api@ecotrace-api",
        }

        message = Message(
            body=body.encode(TASK_CONTENT_ENCODING),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type=TASK_CONTENT_TYPE,
            content_encoding=TASK_CONTENT_ENCODING,
            headers=headers,
        )
        await topic_exchange.publish(message, routing_key=routing_key)
