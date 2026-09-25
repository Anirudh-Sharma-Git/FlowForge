import pytest
from redis.asyncio import Redis

from app.services.redis_service import RedisService


@pytest.mark.asyncio
async def test_redis_connection():

    client = Redis.from_url(
        "redis://localhost:6379/0",
        decode_responses=True,
    )

    service = RedisService(client)

    assert await service.ping()

    await client.aclose()


@pytest.mark.asyncio
async def test_set_get_delete():

    client = Redis.from_url(
        "redis://localhost:6379/0",
        decode_responses=True,
    )

    service = RedisService(client)

    key = "flowforge:test"

    await service.set(
        key,
        "hello",
        expire_seconds=30,
    )

    assert await service.get(key) == "hello"

    assert await service.exists(key)

    await service.delete(key)

    assert not await service.exists(key)

    await client.aclose()