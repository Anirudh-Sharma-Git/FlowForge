from app.services.job_executor import JobExecutor
from app.services.job_repository import PostgresJobRepository


class WorkerRunner:

    def __init__(
        self,
        worker_id: str,
        job_repository: PostgresJobRepository,
    ):
        self.worker_id = worker_id
        self.job_repository = job_repository
        self.executor = JobExecutor()

    async def run_once(self):
        job = await self.job_repository.claim_next_job(
            self.worker_id
        )

        if job is None:
            return None

        try:
            result = await self.executor.execute(job)

            await self.job_repository.complete_job(
                job_id=job.id,
                succeeded=True,
                result=result,
            )

            return {
                "job_id": str(job.id),
                "status": "succeeded",
                "result": result,
            }

        except Exception as exc:

            await self.job_repository.complete_job(
                job_id=job.id,
                succeeded=False,
                error=str(exc),
            )

            return {
                "job_id": str(job.id),
                "status": "failed",
                "error": str(exc),
            }