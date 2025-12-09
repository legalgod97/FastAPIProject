from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from models.users import Base, UserModel
from sqlalchemy import ForeignKey

import sqlalchemy as sa

from models.notifications import NotificationModel
from models.comments import CommentModel
from models.orders import OrderModel


post_like = sa.Table(
    "post_like",
    Base.metadata,
    sa.Column("user_id", sa.ForeignKey("user.id"), primary_key=True),
    sa.Column("post_id", sa.ForeignKey("post.id"), primary_key=True),
)

post_notification = sa.Table(
    "post_notification",
    Base.metadata,
    sa.Column("post_id", sa.ForeignKey("post.id"), primary_key=True),
    sa.Column("notification_id", sa.ForeignKey("notification.id"), primary_key=True),
)

post_order = sa.Table(
    "post_order",
    Base.metadata,
    sa.Column("post_id", sa.ForeignKey("post.id"), primary_key=True),
    sa.Column("order_id", sa.ForeignKey("order.id"), primary_key=True),
)


class PostModel(Base):
    __tablename__ = 'post'

    id: Mapped[UUID] = mapped_column(primary_key=True)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )

    user: Mapped[UserModel] = relationship(
        back_populates="posts",
    )

    author_id: Mapped[UUID] = mapped_column(default=uuid4)
    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    is_published: Mapped[bool] = mapped_column()
    published_at: Mapped[datetime] = mapped_column()

    comments: Mapped[list[CommentModel]] = relationship(
        back_populates="posts",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    notifications: Mapped[list["NotificationModel"]] = relationship(
        secondary=post_notification,
        back_populates="posts",
    )

    orders: Mapped[list["OrderModel"]] = relationship(
        secondary=post_order,
        back_populates="posts",
    )