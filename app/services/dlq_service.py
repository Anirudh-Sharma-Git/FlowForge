from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DeadLetterJobDB


class DeadLetterQueueService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def move_to_dlq(
        self,
        job_id: UUID,
        job_type: str,
        payload: dict,
        error: str | None,
        attempts: int,
    ) -> None:

        from datetime import datetime, timezone

        dead_letter_job = DeadLetterJobDB(
            id=uuid4(),
            job_id=job_id,
            job_type=job_type,
            payload=payload,
            error=error,
            attempts=attempts,
            failed_at=datetime.now(timezone.utc),
        )

        self.session.add(dead_letter_job)
        await self.session.commit()