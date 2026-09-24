import pytest

from app.models.worker import Worker, WorkerStatus


def test_worker_defaults():
    worker = Worker(
        hostname="worker-01",
        capacity=4,
    )

    assert worker.status == WorkerStatus.STARTING
    assert worker.capacity == 4


def test_worker_activation():
    worker = Worker(
        hostname="worker-01",
        capacity=4,
    )

    worker.activate()

    assert worker.status == WorkerStatus.ACTIVE
    assert worker.last_heartbeat_at is not None