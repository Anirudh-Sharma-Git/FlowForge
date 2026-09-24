from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import WorkerDB
from app.models.worker import Worker


class PostgresWorkerRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, worker: Worker) -> Worker:
        worker_db = WorkerDB(
            id=worker.id,
            hostname=worker.hostname,
            capacity=worker.capacity,
            status=worker.status.value,
            registered_at=worker.registered_at,
            last_heartbeat_at=worker.last_heartbeat_at,
        )

        self.session.add(worker_db)
        await self.session.commit()

        return worker

    async def get(self, worker_id: UUID) -> Worker | None:
        worker_db = await self.session.get(WorkerDB, worker_id)

        if worker_db is None:
            return None

        return Worker(
            id=worker_db.id,
            hostname=worker_db.hostname,
            capacity=worker_db.capacity,
            status=worker_db.status,
            registered_at=worker_db.registered_at,
            last_heartbeat_at=worker_db.last_heartbeat_at,
        )

    async def update(self, worker: Worker) -> Worker:
        worker_db = await self.session.get(WorkerDB, worker.id)

        if worker_db is None:
            return worker

        worker_db.hostname = worker.hostname
        worker_db.capacity = worker.capacity
        worker_db.status = worker.status.value
        worker_db.registered_at = worker.registered_at
        worker_db.last_heartbeat_at = worker.last_heartbeat_at

        await self.session.commit()

        return worker