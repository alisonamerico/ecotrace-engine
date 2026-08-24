from abc import ABC, abstractmethod


class MessageBroker(ABC):
    """Port for asynchronous message publishing (infrastructure-agnostic)."""

    @abstractmethod
    async def publish(self, exchange: str, routing_key: str, payload: bytes) -> None:
        """Publish a persistent message to the given exchange and routing key."""
        raise NotImplementedError
