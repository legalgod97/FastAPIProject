from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4

from src.models.base import Base
if TYPE_CHECKING:
    from src.models.profiles import ProfileModel


user_profile = sa.Table(
    "user_profile",
    Base.metadata,
    sa.Column("user_id", sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("profile_id", sa.ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True),
)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    name: Mapped[str] = mapped_column(
        sa.String(length=255),
        nullable=False,
    )

    profile: Mapped["ProfileModel"] = relationship(
        back_populates="user",
        foreign_keys="ProfileModel.user_id",
        uselist=False
    )

    profiles: Mapped[list["ProfileModel"]] = relationship(
        back_populates="owner",
        foreign_keys="ProfileModel.owner_id"
    )

    many_profiles = relationship(
        "ProfileModel",
        secondary=lambda: user_profile,
        back_populates="users",
    )



