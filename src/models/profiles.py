from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from src.models.base import Base
from sqlalchemy import ForeignKey
if TYPE_CHECKING:
    from src.models.users import UserModel


class ProfileModel(Base):
    __tablename__ = "profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id")
    )

    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    user: Mapped["UserModel"] = relationship(
        back_populates="profile",
        foreign_keys=[user_id],
        uselist=False
    )

    owner: Mapped["UserModel"] = relationship(
        back_populates="profiles",
        foreign_keys=[owner_id]
    )


    users = relationship(
        "UserModel",
        secondary=lambda: __import__(
            "src.models.users", fromlist=["user_profile"]
        ).user_profile,
        back_populates="many_profiles",
    )


