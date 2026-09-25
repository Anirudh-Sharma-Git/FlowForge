from aiokafka import AIOKafkaProducer

from app.core.config import settings


producer = AIOKafkaProducer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
)


async def start_kafka() -> None:
    await producer.start()


async def stop_kafka() -> None:
    await producer.stop()