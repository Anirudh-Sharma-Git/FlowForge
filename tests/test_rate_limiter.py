import pytest
from redis.asyncio import Redis

from app.services.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_allows_within_limit():

    redis = Redis.from_url(
        "redis://localhost:6379/0",
        decode_responses=True,
    )

    limiter = RateLimiter(
        redis=redis,
        limit=3,
        window_seconds=60,
    )

    key = "test-user-1"

    await redis.delete(
        f"rate_limit:{key}:{int(__import__('time').time()) // 60}"
    )

    assert await limiter.allow(key)
    assert await limiter.allow(key)
    assert await limiter.allow(key)

    assert not await limiter.allow(key)

    await redis.aclose()


@pytest.mark.asyncio
async def test_rate_limiter_is_independent_per_key():

    redis = Redis.from_url(
        "redis://localhost:6379/0",
        decode_responses=True,
    )

    limiter = RateLimiter(
        redis=redis,
        limit=1,
        window_seconds=60,
    )

    key_a = "test-user-a"
    key_b = "test-user-b"

    assert await limiter.allow(key_a)
    assert not await limiter.allow(key_a)

    assert await limiter.allow(key_b)

    await redis.aclose()