import json
from uuid import uuid4

import pytest

from app.events.job_events import create_job_event
from app.services.event_publisher import EventPublisher


class FakeProducer:

    def __init__(self):
        self.messages = []

    async def send_and_wait(
        self,
        topic,
        key,
        value,
    ):
        self.messages.append(
            {
                "topic": topic,
                "key": key,
                "value": value,
            }
        )


@pytest.mark.asyncio
async def test_event_publisher():

    producer = FakeProducer()

    publisher = EventPublisher(
        producer=producer,
        topic="job-events",
    )

    job_id = uuid4()

    event = create_job_event(
        event_type="job.created",
        job_id=job_id,
        job_type="echo",
        status="queued",
        payload={"message": "hello"},
    )

    await publisher.publish(event)

    assert len(producer.messages) == 1

    message = producer.messages[0]

    assert message["topic"] == "job-events"
    assert message["key"] == str(job_id).encode()

    decoded = json.loads(
        message["value"].decode()
    )

    assert decoded["event_type"] == "job.created"
    assert decoded["job_id"] == str(job_id)
    assert decoded["status"] == "queued"
    assert decoded["payload"]["message"] == "hello"