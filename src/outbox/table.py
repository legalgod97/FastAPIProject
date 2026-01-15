from sqlalchemy import Column, String, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import enum
import uuid

Base = declarative_base()

class OutboxStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"

class OutboxMessage(Base):
    __tablename__ = "outbox"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(Enum(OutboxStatus), nullable=False, default=OutboxStatus.PENDING)