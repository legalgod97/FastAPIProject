from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from src.models.base import Base
if TYPE_CHECKING:
    from src.models.orders import OrderModel


class PostOrderM2M(Base):
    __tablename__ = "posts_orders_m2m"

    post_id: Mapped[UUID] = mapped_column(
        ForeignKey("posts.id"),
        primary_key=True
    )
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id"),
        primary_key=True
    )


class PostModel(Base):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str]
    content: Mapped[str]

    order: Mapped["OrderModel"] = relationship(
        back_populates="post",
        uselist=False,
        cascade="all, delete-orphan"
    )

    orders: Mapped[list["OrderModel"]] = relationship(
        back_populates="post_o2m",
        cascade="all, delete-orphan"
    )

    orders_m2m: Mapped[list["OrderModel"]] = relationship(
        secondary="posts_orders_m2m",
        back_populates="posts_m2m"
    )