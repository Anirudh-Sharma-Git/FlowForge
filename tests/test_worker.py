from datetime import datetime
from uuid import uuid4

import pytest

from app.models.worker import (
    InvalidWorkerTransition,
    Worker,
    WorkerStatus,
)

def test_worker_starts_in_starting_state():
    worker = Worker(
        hostname="worker-01",
        capacity=4,
    )

    assert worker.status == WorkerStatus.STARTING
    assert worker.hostname == "worker-01"
    assert worker.capacity == 4
    assert worker.last_heartbeat_at is None


def test_worker_can_be_activated():
    worker = Worker(
        hostname="worker-01",
        capacity=4,
    )

    worker.activate()

    assert worker.status == WorkerStatus.ACTIVE
    assert worker.last_heartbeat_at is not None


def test_worker_can_begin_draining():
    worker = Worker(
        hostname="worker-01",
        capacity=4,
    )

    worker.activate()
    worker.begin_draining()

    assert worker.status == WorkerStatus.DRAINING


def test_worker_can_go_offline():
    worker = Worker(
        hostname="worker-01",
        capacity=4,
    )

    worker.activate()
    worker.begin_draining()
    worker.mark_offline()

    assert worker.status == WorkerStatus.OFFLINE


def test_worker_heartbeat():
    worker = Worker(
        hostname="worker-01",
        capacity=4,
    )

    worker.activate()

    first_heartbeat = worker.last_heartbeat_at

    worker.heartbeat()

    assert worker.last_heartbeat_at is not None
    assert worker.last_heartbeat_at >= first_heartbeat


def test_draining_worker_can_heartbeat():
    worker = Worker(
        hostname="worker-01",
        capacity=4,
    )

    worker.activate()
    worker.begin_draining()

    worker.heartbeat()

    assert worker.last_heartbeat_at is not None


def test_offline_worker_cannot_become_active():
    worker = Worker(
        hostname="worker-01",
        capacity=4,
    )

    worker.activate()
    worker.mark_offline()

    with pytest.raises(InvalidWorkerTransition):
        worker.activate()


def test_offline_worker_cannot_heartbeat():
    worker = Worker(
        hostname="worker-01",
        capacity=4,
    )

    worker.activate()
    worker.mark_offline()

    with pytest.raises(RuntimeError):
        worker.heartbeat()


