from uuid import UUID

from app.models.job import Job


class InMemoryJobRepository:

    def __init__(self):
        self.jobs: dict[UUID, Job] = {}

    def save(self, job: Job) -> Job:
        self.jobs[job.id] = job
        return job

    def get(self, job_id: UUID) -> Job | None:
        return self.jobs.get(job_id)