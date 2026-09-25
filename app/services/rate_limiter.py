import time

from redis.asyncio import Redis


class RateLimiter:

    def __init__(
        self,
        redis: Redis,
        limit: int,
        window_seconds: int,
    ):
        self.redis = redis
        self.limit = limit
        self.window_seconds = window_seconds

    async def allow(self, key: str) -> bool:
        current_time = int(time.time())
        window = current_time // self.window_seconds

        redis_key = f"rate_limit:{key}:{window}"

        count = await self.redis.incr(redis_key)

        if count == 1:
            await self.redis.expire(
                redis_key,
                self.window_seconds,
            )

        return count <= self.limit