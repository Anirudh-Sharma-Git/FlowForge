import pytest
from redis.asyncio import Redis

from app.services.worker_state import WorkerStateService


@pytest.mark.asyncio
async def test_worker_state():

    redis = Redis.from_url(
        "redis://localhost:6379/0",
        decode_responses=True,
    )

    service = WorkerStateService(redis)

    worker_id = "worker-test-1"

    await service.remove_state(worker_id)

    assert not await service.is_alive(worker_id)

    await service.set_state(
        worker_id,
        "active",
    )

    assert await service.get_state(worker_id) == "active"
    assert await service.is_alive(worker_id)

    await service.set_state(
        worker_id,
        "draining",
    )

    assert await service.get_state(worker_id) == "draining"

    await service.remove_state(worker_id)

    assert not await service.is_alive(worker_id)

    await redis.aclose()