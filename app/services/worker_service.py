from uuid import UUID

from app.models.worker import Worker
from app.services.worker_repository import PostgresWorkerRepository
from app.services.job_repository import PostgresJobRepository


class WorkerService:

    def __init__(
        self,
        worker_repository: PostgresWorkerRepository,
        job_repository: PostgresJobRepository,
    ):
        self.worker_repository = worker_repository
        self.job_repository = job_repository

    async def register_worker(
        self,
        hostname: str,
        capacity: int,
    ) -> Worker:

        worker = Worker(
            hostname=hostname,
            capacity=capacity,
        )

        worker.activate()

        await self.worker_repository.save(worker)

        return worker

    async def heartbeat(
        self,
        worker_id: UUID,
    ) -> Worker | None:

        worker = await self.worker_repository.get(worker_id)

        if worker is None:
            return None

        worker.heartbeat()

        await self.worker_repository.update(worker)

        return worker

    async def drain_worker(
        self,
        worker_id: UUID,
    ) -> Worker | None:

        worker = await self.worker_repository.get(worker_id)

        if worker is None:
            return None

        worker.begin_draining()

        await self.worker_repository.update(worker)

        return worker

    async def claim_job(
        self,
        worker_id: str,
    ):
        return await self.job_repository.claim_next_job(worker_id)