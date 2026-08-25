import fakeredis.aioredis
import pytest

from app.infrastructure.cache.redis_lock import RedisLockManager


@pytest.fixture
async def redis():
    server = fakeredis.aioredis.FakeServer()
    client = fakeredis.aioredis.FakeRedis(server=server)
    yield client
    await client.aclose()


@pytest.fixture
def lock_manager(redis):
    return RedisLockManager(redis_client=redis)


async def test_acquire_returns_true_on_first_call(lock_manager):
    result = await lock_manager.acquire("lock:nfe:abc123", ttl_seconds=10)
    assert result is True


async def test_acquire_returns_false_when_key_already_held(lock_manager):
    await lock_manager.acquire("lock:nfe:abc123", ttl_seconds=10)
    result = await lock_manager.acquire("lock:nfe:abc123", ttl_seconds=10)
    assert result is False


async def test_release_allows_reacquire(lock_manager):
    await lock_manager.acquire("lock:nfe:abc123", ttl_seconds=10)
    await lock_manager.release("lock:nfe:abc123")
    result = await lock_manager.acquire("lock:nfe:abc123", ttl_seconds=10)
    assert result is True


async def test_release_nonexistent_lock_does_not_raise(lock_manager):
    await lock_manager.release("lock:nfe:does-not-exist")


async def test_different_keys_are_independent(lock_manager):
    assert await lock_manager.acquire("lock:nfe:key1", ttl_seconds=10) is True
    assert await lock_manager.acquire("lock:nfe:key2", ttl_seconds=10) is True
