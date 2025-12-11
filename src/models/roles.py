from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.users import Base
from models.profiles import ProfileModel


class RoleProfileM2M(Base):
    __tablename__ = "roles_profiles_m2m"

    role_id: Mapped[UUID] = mapped_column(
        ForeignKey("roles.id"),
        primary_key=True
    )

    profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("profiles.id"),
        primary_key=True,
    )


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    description: Mapped[str]

    profile: Mapped["ProfileModel"] = relationship(
        back_populates="role",
        uselist=False,
        cascade="all, delete-orphan"
    )

    profiles: Mapped[list["ProfileModel"]] = relationship(
        back_populates="role_o2m",
        cascade="all, delete-orphan"
    )

    profiles_m2m: Mapped[list["ProfileModel"]] = relationship(
        secondary="roles_profiles_m2m",
        back_populates="roles_m2m"
    )
