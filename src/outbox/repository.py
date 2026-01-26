from sqlalchemy import select, update
from .table import OutboxMessage, OutboxStatus

class OutboxRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def add(self, topic: str, payload: dict) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                msg = OutboxMessage(topic=topic, payload=payload)
                session.add(msg)

    async def get_pending(self) -> list[OutboxMessage]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(OutboxMessage).where(OutboxMessage.status == OutboxStatus.PENDING)
            )
            return result.scalars().all()

    async def mark_sent(self, message_id) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(OutboxMessage)
                .where(OutboxMessage.id == message_id)
                .values(status=OutboxStatus.SENT)
            )

