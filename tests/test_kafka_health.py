import pytest

from app.services.kafka_health import KafkaHealthService


class FakeKafkaClient:

    async def list_topics(self):
        return {"job-events"}


class FakeProducer:

    def __init__(self):
        self.client = FakeKafkaClient()


@pytest.mark.asyncio
async def test_kafka_health():

    service = KafkaHealthService(
        FakeProducer()
    )

    assert await service.is_healthy()