from uuid import UUID

from app.models.job import Job
from app.schemas.job import JobCreate


class JobService:

    def __init__(self, repository):
        self.repository = repository

    async def create_job(self, job_data: JobCreate) -> Job:
        job = Job(
            type=job_data.type,
            payload=job_data.payload,
            priority=job_data.priority,
        )

        await self.repository.save(job)

        return job

    async def get_job(self, job_id: UUID) -> Job | None:
        return await self.repository.get(job_id)