from uuid import UUID

from app.models.worker import Worker
from app.services.worker_repository import PostgresWorkerRepository


class WorkerService:

    def __init__(self, repository: PostgresWorkerRepository):
        self.repository = repository

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

        await self.repository.save(worker)

        return worker

    async def heartbeat(self, worker_id: UUID) -> Worker | None:
        worker = await self.repository.get(worker_id)

        if worker is None:
            return None

        worker.heartbeat()

        await self.repository.update(worker)

        return worker

    async def drain_worker(self, worker_id: UUID) -> Worker | None:
        worker = await self.repository.get(worker_id)

        if worker is None:
            return None

        worker.begin_draining()

        await self.repository.update(worker)

        return worker