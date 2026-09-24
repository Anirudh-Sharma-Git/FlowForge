from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import JobDB
from app.models.job import Job
from app.db.models import ExecutionAttemptDB
from app.models.execution_attempt import ExecutionAttempt


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

    async def claim_next_job(self) -> Job | None:
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

        async def create_attempt(
        self,
        job_id: UUID,
        attempt_number: int,
    ) -> ExecutionAttempt:

            attempt = ExecutionAttempt(
                job_id=job_id,
                attempt_number=attempt_number,
            )

            attempt_db = ExecutionAttemptDB(
                id=attempt.id,
                job_id=attempt.job_id,
                attempt_number=attempt.attempt_number,
                status=attempt.status.value,
            )

            self.session.add(attempt_db)
            await self.session.commit()

            return attempt   