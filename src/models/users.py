from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeMeta, Mapped, declarative_base, mapped_column, relationship
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
    name: Mapped[str] = mapped_column()

    profile: Mapped["ProfileModel"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    profiles: Mapped[list["ProfileModel"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    many_profiles: Mapped[list["ProfileModel"]] = relationship(
        secondary="user_profile",
        back_populates="many_users"
    )


