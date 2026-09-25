from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OutboxEventDB


class OutboxRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        event_type: str,
        aggregate_id: UUID,
        topic: str,
        payload: dict,
    ) -> OutboxEventDB:

        event = OutboxEventDB(
            event_type=event_type,
            aggregate_id=aggregate_id,
            topic=topic,
            payload=payload,
            created_at=datetime.now(timezone.utc),
        )

        self.session.add(event)

        return event

    async def get_pending(
        self,
        limit: int = 100,
    ) -> list[OutboxEventDB]:

        result = await self.session.execute(
            select(OutboxEventDB)
            .where(
                OutboxEventDB.published_at.is_(None)
            )
            .order_by(
                OutboxEventDB.created_at
            )
            .limit(limit)
        )

        return list(result.scalars().all())

    async def mark_published(
        self,
        event: OutboxEventDB,
    ) -> None:

        event.published_at = datetime.now(timezone.utc)

    async def mark_failed(
        self,
        event: OutboxEventDB,
        error: str,
    ) -> None:

        event.attempts += 1
        event.last_error = error

    async def save(self) -> None:
        await self.session.commit()