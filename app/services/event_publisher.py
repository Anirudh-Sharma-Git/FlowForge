import json

from aiokafka import AIOKafkaProducer

from app.events.job_events import JobEvent


class EventPublisher:

    def __init__(
        self,
        producer: AIOKafkaProducer,
        topic: str,
    ):
        self.producer = producer
        self.topic = topic

    async def publish(
        self,
        event: JobEvent,
        topic: str | None = None,
    ) -> None:

        value = json.dumps(
            event.to_dict()
        ).encode("utf-8")

        target_topic = topic or self.topic

        await self.producer.send_and_wait(
            target_topic,
            key=str(event.job_id).encode("utf-8"),
            value=value,
        )