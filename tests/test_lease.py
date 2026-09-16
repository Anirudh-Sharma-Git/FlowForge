from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.models.lease import Lease

def test_lease_starts_without_expiration():
    lease = Lease(
        job_id=uuid4(),
        attempt_id=uuid4(),
        worker_id="worker-01",
    )

    assert lease.expires_at is None
    assert lease.last_heartbeat_at is None
    assert lease.is_expired()

def test_acquire_lease():
    lease = Lease(
        job_id=uuid4(),
        attempt_id=uuid4(),
        worker_id="worker-01",
    )

    lease.acquire()

    assert lease.expires_at is not None
    assert lease.last_heartbeat_at is not None
    assert not lease.is_expired()

def test_renew_lease():
    lease = Lease(
        job_id=uuid4(),
        attempt_id=uuid4(),
        worker_id="worker-01",
    )

    lease.acquire()

    old_expiry = lease.expires_at

    lease.renew()

    assert lease.expires_at > old_expiry
    assert not lease.is_expired()


def test_expired_lease():
    lease = Lease(
        job_id=uuid4(),
        attempt_id=uuid4(),
        worker_id="worker-01",
    )

    lease.acquire()

    lease.expires_at = (
        datetime.now(timezone.utc) - timedelta(seconds=1)
    )

    assert lease.is_expired()


def test_expired_lease_cannot_be_renewed():
    lease = Lease(
        job_id=uuid4(),
        attempt_id=uuid4(),
        worker_id="worker-01",
    )

    lease.acquire()

    lease.expires_at = (
        datetime.now(timezone.utc) - timedelta(seconds=1)
    )

    with pytest.raises(RuntimeError):
        lease.renew()

