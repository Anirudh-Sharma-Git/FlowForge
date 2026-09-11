import pytest

from app.models.job import (
    InvalidJobTransition,
    JobStateMachine,
    JobStatus,
)


def test_pending_can_be_queued():
    assert JobStateMachine.can_transition(
        JobStatus.PENDING,
        JobStatus.QUEUED,
    )


def test_queued_can_be_running():
    assert JobStateMachine.can_transition(
        JobStatus.QUEUED,
        JobStatus.RUNNING,
    )


def test_running_can_succeed():
    assert JobStateMachine.can_transition(
        JobStatus.RUNNING,
        JobStatus.SUCCEEDED,
    )


def test_running_can_fail():
    assert JobStateMachine.can_transition(
        JobStatus.RUNNING,
        JobStatus.FAILED,
    )


def test_failed_can_retry():
    assert JobStateMachine.can_transition(
        JobStatus.FAILED,
        JobStatus.QUEUED,
    )


def test_pending_cannot_be_running():
    assert not JobStateMachine.can_transition(
        JobStatus.PENDING,
        JobStatus.RUNNING,
    )


def test_succeeded_cannot_be_running():
    assert not JobStateMachine.can_transition(
        JobStatus.SUCCEEDED,
        JobStatus.RUNNING,
    )


def test_cancelled_cannot_be_queued():
    assert not JobStateMachine.can_transition(
        JobStatus.CANCELLED,
        JobStatus.QUEUED,
    )


def test_invalid_transition_raises():
    with pytest.raises(InvalidJobTransition):
        JobStateMachine.transition(
            JobStatus.SUCCEEDED,
            JobStatus.RUNNING,
        )


from app.models.job import (
    InvalidJobTransition,
    Job,
    JobStatus,
)


def test_new_job_starts_pending():
    job = Job(
        type="image_resize",
        payload={"image": "cat.jpg"},
    )

    assert job.status == JobStatus.PENDING
    assert job.priority == 0
    assert job.max_attempts == 3
    assert job.version == 1


def test_job_can_transition():
    job = Job(
        type="image_resize",
        payload={"image": "cat.jpg"},
    )

    job.transition_to(JobStatus.QUEUED)

    assert job.status == JobStatus.QUEUED
    assert job.version == 2


def test_invalid_transition_raises():
    job = Job(
        type="image_resize",
        payload={"image": "cat.jpg"},
    )

    with pytest.raises(InvalidJobTransition):
        job.transition_to(JobStatus.RUNNING)


def test_each_job_gets_unique_id():
    job_a = Job(
        type="test",
        payload={},
    )

    job_b = Job(
        type="test",
        payload={},
    )

    assert job_a.id != job_b.id