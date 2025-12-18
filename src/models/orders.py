from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base
from uuid import UUID, uuid4
if TYPE_CHECKING:
    from src.models.posts import PostModel


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    price: Mapped[int]

    post_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("posts.id"),
        unique=True
    )
    post: Mapped["PostModel"] = relationship(
        back_populates="order"
    )

    post_o2m_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("posts.id")
    )
    post_o2m: Mapped["PostModel"] = relationship(
        back_populates="orders"
    )

    posts_m2m: Mapped[list["PostModel"]] = relationship(
        secondary="posts_orders_m2m",
        back_populates="orders_m2m"
    )