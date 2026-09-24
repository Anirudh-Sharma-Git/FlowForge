from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import JobDB
from app.models.job import Job


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