from app.models.job import Job
from app.schemas.job import JobCreate
from app.services.job_repository import InMemoryJobRepository


class JobService:

    def __init__(self, repository: InMemoryJobRepository):
        self.repository = repository

    def create_job(self, job_data: JobCreate) -> Job:

        job = Job(
            type=job_data.type,
            payload=job_data.payload,
            priority=job_data.priority,
        )

        self.repository.save(job)

        return job