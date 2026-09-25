from redis.asyncio import Redis


class RedisService:

    def __init__(self, client: Redis):
        self.client = client

    async def set(
        self,
        key: str,
        value: str,
        expire_seconds: int | None = None,
    ) -> None:

        await self.client.set(
            key,
            value,
            ex=expire_seconds,
        )

    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key))

    async def ping(self) -> bool:
        return bool(await self.client.ping())