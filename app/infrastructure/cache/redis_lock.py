from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redis.asyncio import Redis


class RedisLockManager:
    """Distributed lock via Redis SET NX EX (RF02 — Idempotency)."""

    def __init__(self, redis_client: Redis) -> None:
        self._redis = redis_client
        self._tokens: dict[str, str] = {}

    async def acquire(self, lock_key: str, ttl_seconds: int) -> bool:
        token = secrets.token_urlsafe(24)
        acquired = await self._redis.set(lock_key, token, nx=True, ex=ttl_seconds)
        if acquired:
            self._tokens[lock_key] = token
        return bool(acquired)

    async def release(self, lock_key: str) -> None:
        token = self._tokens.pop(lock_key, None)
        if token is not None:
            stored = await self._redis.get(lock_key)
            stored_str = stored.decode() if isinstance(stored, bytes) else stored
            if stored_str == token:
                await self._redis.delete(lock_key)
