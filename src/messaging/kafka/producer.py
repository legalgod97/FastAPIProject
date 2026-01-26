import json
from aiokafka import AIOKafkaProducer
from src.config.kafka import KafkaSettings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from src.exceptions.common import ProducerError
from src.outbox.table import OutboxMessage, OutboxStatus


class KafkaProducer:
    def __init__(
        self,
        settings: KafkaSettings,
        session_factory,
        dlq_topic: str | None = None,
    ):
        self._settings = settings
        self._producer: AIOKafkaProducer | None = None
        self._session_factory = session_factory
        self._dlq_topic = dlq_topic

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._settings.bootstrap_servers,
            acks="all",
            enable_idempotence=True,
        )
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()

    async def publish(self, topic: str, payload: dict, key: str | None = None) -> None:
        if not self._producer:
            raise ProducerError("Producer is not started")

        await self._producer.send_and_wait(
            topic,
            json.dumps(payload).encode("utf-8"),
            key=key.encode() if key else None,
        )

    async def flush_outbox(self) -> None:
        if not self._producer:
            raise ProducerError("Producer is not started")

        async with self._session_factory() as session:  # type: AsyncSession
            result = await session.execute(
                OutboxMessage.__table__.select().where(OutboxMessage.status == OutboxStatus.PENDING)
            )
            messages = result.fetchall()

            for msg in messages:
                try:
                    await self.publish(msg.topic, msg.payload, key=str(msg.id))
                    await session.execute(
                        update(OutboxMessage)
                        .where(OutboxMessage.id == msg.id)
                        .values(status=OutboxStatus.SENT)
                    )
                except ProducerError as exc:
                    if self._dlq_topic:
                        await self.publish(
                            topic=self._dlq_topic,
                            payload={
                                "error_type": type(exc).__name__,
                                "error": exc.detail,
                                "original": msg.payload,
                            },
                            key=str(msg.id),
                        )

