from typing import Callable, Awaitable, Any, Optional, List

import ujson
from aiokafka import AIOKafkaProducer
from src.config.kafka import KafkaSettings
from sqlalchemy import update, select

from src.exceptions.common import ProducerError
from src.outbox.table import OutboxMessage, OutboxStatus

BATCH_SIZE = 100

class KafkaProducer:
    def __init__(
        self,
        settings: KafkaSettings,
        session_factory: Callable[..., Awaitable[Any]],
        dlq_topic: str | None = None,
    ):
        self._settings: KafkaSettings = settings
        self._producer: AIOKafkaProducer | None = None
        self._session_factory: Callable[..., Awaitable[Any]] = session_factory
        self._dlq_topic: Optional[str] = dlq_topic

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
            ujson.dumps(payload).encode("utf-8"),
            key=key.encode() if key else None,
        )

    async def flush_outbox(self) -> None:
        if not self._producer:
            raise ProducerError("Producer is not started")

        async with self._session_factory() as session:
            while True:
                stmt = (
                    select(OutboxMessage)
                    .where(OutboxMessage.status == OutboxStatus.PENDING)
                    .limit(BATCH_SIZE)
                    .with_for_update(skip_locked=True)
                )

                result = await session.execute(stmt)
                messages: List[OutboxMessage] = result.scalars().all()

                if not messages:
                    break

                ids = [msg.id for msg in messages]

                await session.execute(
                    update(OutboxMessage)
                    .where(OutboxMessage.id.in_(ids))
                    .values(status=OutboxStatus.PROCESSING)
                )

                await session.commit()

                for msg in messages:
                    try:
                        await self.publish(
                            topic=msg.topic,
                            payload=msg.payload,
                            key=str(msg.id),
                        )

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

                        await session.execute(
                            update(OutboxMessage)
                            .where(OutboxMessage.id == msg.id)
                            .values(status=OutboxStatus.FAILED)
                        )

                await session.commit()

