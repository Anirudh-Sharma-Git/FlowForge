from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    DeadLetterJobDB,
    ExecutionAttemptDB,
    JobDB,
    LeaseDB,
    OutboxEventDB,
)
from app.models.execution_attempt import ExecutionAttempt
from app.models.job import Job
from app.models.lease import Lease
from app.services.retry_policy import RetryPolicy


class PostgresJobRepository:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.retry_policy = RetryPolicy()

    async def save(self, job: Job) -> Job:
        job_db = JobDB(
            id=job.id,
            type=job.type,
            payload=job.payload,
            status=job.status.value,
            priority=job.priority,
            max_attempts=job.max_attempts,
            version=job.version,
            created_at=job.created_at,
            updated_at=job.updated_at,
            next_attempt_at=job.next_attempt_at,
        )

        self.session.add(job_db)
        await self.session.commit()

        return job

    async def get(self, job_id: UUID) -> Job | None:
        job_db = await self.session.get(JobDB, job_id)

        if job_db is None:
            return None

        return Job(
            id=job_db.id,
            type=job_db.type,
            payload=job_db.payload,
            status=job_db.status,
            priority=job_db.priority,
            max_attempts=job_db.max_attempts,
            created_at=job_db.created_at,
            updated_at=job_db.updated_at,
            next_attempt_at=job_db.next_attempt_at,
            version=job_db.version,
        )

    async def get_queued_jobs(self) -> list[Job]:
        result = await self.session.execute(
            select(JobDB)
            .where(JobDB.status == "queued")
            .order_by(JobDB.priority.desc())
        )

        rows = result.scalars().all()

        return [
            Job(
                id=row.id,
                type=row.type,
                payload=row.payload,
                status=row.status,
                priority=row.priority,
                max_attempts=row.max_attempts,
                created_at=row.created_at,
                updated_at=row.updated_at,
                next_attempt_at=row.next_attempt_at,
                version=row.version,
            )
            for row in rows
        ]

    async def claim_next_job(
        self,
        worker_id: str,
    ) -> Job | None:

        async with self.session.begin():

            now = datetime.now(timezone.utc)

            result = await self.session.execute(
                select(JobDB)
                .where(JobDB.status == "queued")
                .where(
                    (JobDB.next_attempt_at.is_(None))
                    | (JobDB.next_attempt_at <= now)
                )
                .order_by(JobDB.priority.desc())
                .with_for_update(skip_locked=True)
                .limit(1)
            )

            job_db = result.scalar_one_or_none()

            if job_db is None:
                return None

            attempt_count_result = await self.session.execute(
                select(func.count(ExecutionAttemptDB.id))
                .where(
                    ExecutionAttemptDB.job_id == job_db.id
                )
            )

            attempt_number = (
                attempt_count_result.scalar_one() + 1
            )

            job_db.status = "running"
            job_db.version += 1
            job_db.next_attempt_at = None

            attempt = ExecutionAttempt(
                job_id=job_db.id,
                attempt_number=attempt_number,
            )

            attempt.start(worker_id)

            attempt_db = ExecutionAttemptDB(
                id=attempt.id,
                job_id=attempt.job_id,
                attempt_number=attempt.attempt_number,
                status=attempt.status.value,
                worker_id=attempt.worker_id,
                started_at=attempt.started_at,
            )

            self.session.add(attempt_db)

            lease = Lease(
                job_id=job_db.id,
                attempt_id=attempt.id,
                worker_id=worker_id,
            )

            lease.acquire()

            lease_db = LeaseDB(
                id=lease.id,
                job_id=lease.job_id,
                attempt_id=lease.attempt_id,
                worker_id=lease.worker_id,
                acquired_at=lease.acquired_at,
                expires_at=lease.expires_at,
                last_heartbeat_at=lease.last_heartbeat_at,
                duration_seconds=lease.duration_seconds,
            )

            self.session.add(lease_db)

            return Job(
                id=job_db.id,
                type=job_db.type,
                payload=job_db.payload,
                status=job_db.status,
                priority=job_db.priority,
                max_attempts=job_db.max_attempts,
                created_at=job_db.created_at,
                updated_at=job_db.updated_at,
                next_attempt_at=job_db.next_attempt_at,
                version=job_db.version,
            )

    async def complete_job(
        self,
        job_id: UUID,
        succeeded: bool,
        result: dict | None = None,
        error: str | None = None,
    ) -> None:

        async with self.session.begin():

            job_db = await self.session.get(
                JobDB,
                job_id,
                with_for_update=True,
            )

            if job_db is None:
                return

            attempt_result = await self.session.execute(
                select(ExecutionAttemptDB)
                .where(
                    ExecutionAttemptDB.job_id == job_id
                )
                .order_by(
                    ExecutionAttemptDB.attempt_number.desc()
                )
                .limit(1)
            )

            attempt_db = attempt_result.scalar_one_or_none()

            if attempt_db is None:
                return

            now = datetime.now(timezone.utc)

            if succeeded:

                job_db.status = "succeeded"

                attempt_db.status = "succeeded"
                attempt_db.result = result
                attempt_db.error = None
                attempt_db.finished_at = now

                job_db.next_attempt_at = None

                event = OutboxEventDB(
                    id=uuid4(),
                    event_type="job.succeeded",
                    aggregate_id=job_db.id,
                    topic="job-events",
                    payload={
                        "job_id": str(job_db.id),
                        "job_type": job_db.type,
                        "status": "succeeded",
                        "result": result,
                        "attempt_number": attempt_db.attempt_number,
                    },
                    created_at=now,
                )

                self.session.add(event)

            else:

                attempt_db.status = "failed"
                attempt_db.error = error
                attempt_db.result = None
                attempt_db.finished_at = now

                if attempt_db.attempt_number < job_db.max_attempts:

                    delay = self.retry_policy.get_delay(
                        attempt_db.attempt_number
                    )

                    job_db.status = "queued"

                    job_db.next_attempt_at = (
                        now + timedelta(seconds=delay)
                    )

                    event = OutboxEventDB(
                        id=uuid4(),
                        event_type="job.retry_scheduled",
                        aggregate_id=job_db.id,
                        topic="job-events",
                        payload={
                            "job_id": str(job_db.id),
                            "job_type": job_db.type,
                            "status": "queued",
                            "error": error,
                            "attempt_number": attempt_db.attempt_number,
                            "next_attempt_at": (
                                job_db.next_attempt_at.isoformat()
                            ),
                        },
                        created_at=now,
                    )

                    self.session.add(event)

                else:

                    job_db.status = "failed"
                    job_db.next_attempt_at = None

                    dlq_entry = DeadLetterJobDB(
                        id=uuid4(),
                        job_id=job_db.id,
                        job_type=job_db.type,
                        payload=job_db.payload,
                        error=error,
                        attempts=attempt_db.attempt_number,
                        failed_at=now,
                    )

                    self.session.add(dlq_entry)

                    event = OutboxEventDB(
                        id=uuid4(),
                        event_type="job.failed",
                        aggregate_id=job_db.id,
                        topic="job-events",
                        payload={
                            "job_id": str(job_db.id),
                            "job_type": job_db.type,
                            "status": "failed",
                            "error": error,
                            "attempt_number": attempt_db.attempt_number,
                            "dead_letter": True,
                        },
                        created_at=now,
                    )

                    self.session.add(event)

            job_db.version += 1
            job_db.updated_at = now

            await self.session.execute(
                delete(LeaseDB).where(
                    LeaseDB.attempt_id == attempt_db.id
                )
            )