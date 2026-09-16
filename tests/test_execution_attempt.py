from uuid import uuid4

import pytest

from app.models.execution_attempt import (
    AttemptStatus,
    ExecutionAttempt,
    InvalidAttemptTransition,
)

def test_attempt_starts_pending():
    attempt = ExecutionAttempt(
        job_id=uuid4(),
        attempt_number=1,
    )

    assert attempt.status == AttemptStatus.PENDING
    assert attempt.worker_id is None
    assert attempt.started_at is None
    assert attempt.finished_at is None

def test_attempt_can_succeed():
    attempt = ExecutionAttempt(
        job_id=uuid4(),
        attempt_number=1,
    )

    attempt.start("worker-01")
    attempt.succeed({"message": "done"})

    assert attempt.status == AttemptStatus.SUCCEEDED
    assert attempt.worker_id == "worker-01"
    assert attempt.started_at is not None
    assert attempt.finished_at is not None
    assert attempt.result == {"message": "done"}

def test_attempt_can_fail():
    attempt = ExecutionAttempt(
        job_id=uuid4(),
        attempt_number=1,
    )

    attempt.start("worker-01")
    attempt.fail("worker crashed")

    assert attempt.status == AttemptStatus.FAILED
    assert attempt.error == "worker crashed"
    assert attempt.finished_at is not None

def test_invalid_attempt_transition():
    attempt = ExecutionAttempt(
        job_id=uuid4(),
        attempt_number=1,
    )

    with pytest.raises(InvalidAttemptTransition):
        attempt.succeed()

def test_succeeded_attempt_cannot_run_again():
    attempt = ExecutionAttempt(
        job_id=uuid4(),
        attempt_number=1,
    )

    attempt.start("worker-01")
    attempt.succeed()

    with pytest.raises(InvalidAttemptTransition):
        attempt.start("worker-02")