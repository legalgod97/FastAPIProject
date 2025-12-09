import enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.users import Base
from uuid import UUID
from models.orders import OrderModel
from sqlalchemy import ForeignKey
from models.posts import PostModel, post_notification


class TypeStatus(enum.Enum):
    system = "system"
    marketing = "marketing"
    personal = "personal"

class NotificationModel(Base):
    __tablename__ = 'notification'
    id: Mapped[UUID] = mapped_column(primary_key=True)

    order_id: Mapped[UUID] = mapped_column(
        ForeignKey('order.id'),
        unique=True,
        nullable=False,
        ondelete="CASCADE",
    )

    message: Mapped[str] = mapped_column()
    type: Mapped[TypeStatus] = mapped_column()
    is_read: Mapped[bool] = mapped_column(default=False)
    read_at: Mapped[datetime] = mapped_column()

    order: Mapped[OrderModel] = relationship(
        back_populates="notification",
        uselist=False
    )

    posts: Mapped[list["PostModel"]] = relationship(
        secondary=post_notification,
        back_populates="notifications",
    )
