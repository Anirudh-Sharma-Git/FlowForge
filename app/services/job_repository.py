from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ExecutionAttemptDB, JobDB, LeaseDB
from app.models.execution_attempt import ExecutionAttempt
from app.models.job import Job
from app.models.lease import Lease


class PostgresJobRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

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
                version=row.version,
            )
            for row in rows
        ]

    async def claim_next_job(
        self,
        worker_id: str,
    ) -> Job | None:

        async with self.session.begin():
            result = await self.session.execute(
                select(JobDB)
                .where(JobDB.status == "queued")
                .order_by(JobDB.priority.desc())
                .with_for_update(skip_locked=True)
                .limit(1)
            )

            job_db = result.scalar_one_or_none()

            if job_db is None:
                return None

            job_db.status = "running"
            job_db.version += 1

            attempt = ExecutionAttempt(
                job_id=job_db.id,
                attempt_number=1,
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
                version=job_db.version,
            )