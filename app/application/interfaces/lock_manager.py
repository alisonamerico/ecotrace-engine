from abc import ABC, abstractmethod


class LockManager(ABC):
    """Port for distributed lock acquisition (RF02 — Idempotency via Distributed Lock)."""

    @abstractmethod
    async def acquire(self, lock_key: str, ttl_seconds: int) -> bool:
        """Try to acquire a distributed lock. Returns True on success."""
        raise NotImplementedError

    @abstractmethod
    async def release(self, lock_key: str) -> None:
        """Release a previously acquired lock."""
        raise NotImplementedError
