from redis.asyncio import Redis


class WorkerStateService:

    def __init__(self, redis: Redis):
        self.redis = redis

    def _key(self, worker_id: str) -> str:
        return f"worker:{worker_id}:state"

    async def set_state(
        self,
        worker_id: str,
        state: str,
        expire_seconds: int = 30,
    ) -> None:

        await self.redis.set(
            self._key(worker_id),
            state,
            ex=expire_seconds,
        )

    async def get_state(
        self,
        worker_id: str,
    ) -> str | None:

        return await self.redis.get(
            self._key(worker_id)
        )

    async def remove_state(
        self,
        worker_id: str,
    ) -> None:

        await self.redis.delete(
            self._key(worker_id)
        )

    async def is_alive(
        self,
        worker_id: str,
    ) -> bool:

        return bool(
            await self.redis.exists(
                self._key(worker_id)
            )
        )