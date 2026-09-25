from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.db.models import (
    ExecutionAttemptDB,
    JobDB,
    OutboxEventDB,
)
from app.services.job_repository import PostgresJobRepository


@pytest.mark.asyncio
async def test_complete_job_creates_outbox_event(db_session):

    job_id = uuid4()
    attempt_id = uuid4()

    now = datetime.now(timezone.utc)

    job = JobDB(
        id=job_id,
        type="echo",
        payload={"message": "hello"},
        status="running",
        priority=1,
        max_attempts=3,
        version=1,
        created_at=now,
        updated_at=now,
    )

    attempt = ExecutionAttemptDB(
        id=attempt_id,
        job_id=job_id,
        attempt_number=1,
        status="running",
        worker_id="worker-1",
        started_at=now,
    )

    db_session.add(job)
    db_session.add(attempt)

    await db_session.commit()

    repository = PostgresJobRepository(db_session)

    result = await repository.complete_job(
        job_id=job_id,
        succeeded=True,
        result={"message": "hello"},
    )

    assert result is None

    query = (
        select(OutboxEventDB)
        .where(
            OutboxEventDB.aggregate_id == job_id
        )
    )

    query_result = await db_session.execute(query)

    event = query_result.scalar_one()

    assert event.event_type == "job.succeeded"
    assert event.aggregate_id == job_id
    assert event.topic == "job-events"
    assert event.published_at is None

    updated_job = await db_session.get(
        JobDB,
        job_id,
    )

    assert updated_job.status == "succeeded"

    updated_attempt = await db_session.get(
        ExecutionAttemptDB,
        attempt_id,
    )

    assert updated_attempt.status == "succeeded"
    assert updated_attempt.result == {"message": "hello"}