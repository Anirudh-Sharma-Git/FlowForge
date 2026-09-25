import asyncio
import logging

from app.core.kafka import producer
from app.db.session import AsyncSessionLocal
from app.events.job_events import JobEvent
from app.services.event_publisher import EventPublisher
from app.services.outbox_repository import OutboxRepository


logger = logging.getLogger(__name__)


class OutboxPublisher:

    def __init__(
        self,
        batch_size: int = 100,
        poll_interval: float = 1.0,
    ):
        self.batch_size = batch_size
        self.poll_interval = poll_interval

        self.event_publisher = EventPublisher(
            producer=producer,
            topic="job-events",
        )

    async def publish_pending(self) -> None:

        async with AsyncSessionLocal() as session:

            repository = OutboxRepository(session)

            events = await repository.get_pending(
                limit=self.batch_size
            )

            for event in events:

                try:
                    payload = event.payload or {}

                    job_event = JobEvent(
                        event_type=event.event_type,
                        job_id=event.aggregate_id,
                        job_type=payload["job_type"],
                        status=payload["status"],
                        timestamp=event.created_at,
                        payload=payload.get("result"),
                        error=payload.get("error"),
                    )

                    await self.event_publisher.publish(
                        job_event,
                        topic=event.topic,
                    )

                    await repository.mark_published(
                        event
                    )

                except asyncio.CancelledError:
                    raise

                except Exception as exc:

                    logger.exception(
                        "Failed to publish outbox event %s",
                        event.id,
                    )

                    await repository.mark_failed(
                        event,
                        str(exc),
                    )

            await repository.save()

    async def run(self) -> None:

        while True:

            try:
                await self.publish_pending()

            except asyncio.CancelledError:
                raise

            except Exception:
                logger.exception(
                    "Outbox publisher iteration failed"
                )

            await asyncio.sleep(
                self.poll_interval
            )