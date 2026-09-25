from aiokafka import AIOKafkaProducer


class KafkaHealthService:

    def __init__(self, producer: AIOKafkaProducer):
        self.producer = producer

    async def is_healthy(self) -> bool:
        try:
            await self.producer.client.list_topics()
            return True
        except Exception:
            return False