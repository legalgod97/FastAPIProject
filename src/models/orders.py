import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.users import Base, UserModel
from uuid import UUID
from src.models.notifications import NotificationModel
from src.models.posts import PostModel, post_order


class OrderStatus(enum.Enum):
    created = "created"
    paid = "paid"
    cancelled = "cancelled"
    shipped = "shipped"

class OrderModel(Base):
    __tablename__ = 'order'
    id: Mapped[UUID] = mapped_column(primary_key=True)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"),
        ondelete="CASCADE",
        nullable=False
    )

    total_amount: Mapped[Decimal] = mapped_column()
    status: Mapped[OrderStatus] = mapped_column()
    payment_method: Mapped[str] = mapped_column()
    paid_at: Mapped[datetime] = mapped_column()

    notification: Mapped[NotificationModel] = relationship(
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    user: Mapped[UserModel] = relationship(
        back_populates="orders",
    )

    posts: Mapped[list["PostModel"]] = relationship(
        secondary=post_order,
        back_populates="orders",
    )