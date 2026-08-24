
from fastapi import Request

from app.application.interfaces.message_broker import MessageBroker
from app.infrastructure.database.session import get_db_session

get_session = get_db_session


def get_message_broker(request: Request) -> MessageBroker:
    """Return the application-scoped event publisher wired in the lifespan."""
    broker: MessageBroker = request.app.state.message_publisher
    return broker
