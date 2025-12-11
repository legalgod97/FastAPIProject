from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from models.roles import RoleModel
from models.users import Base
from sqlalchemy import ForeignKey
from models.users import UserModel


class ProfileModel(Base):
    __tablename__ = "profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    full_name: Mapped[str]
    bio: Mapped[str]

    owner_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user.id")
    )
    owner: Mapped["UserModel"] = relationship(
        back_populates="profiles"
    )

    role_id: Mapped[UUID | None] = mapped_column(ForeignKey("roles.id"), unique=True)
    role: Mapped["RoleModel"] = relationship(back_populates="profile")

    role_o2m_id: Mapped[UUID | None] = mapped_column(ForeignKey("roles.id"))
    role_o2m: Mapped["RoleModel"] = relationship(back_populates="profiles")

    roles_m2m: Mapped[list["RoleModel"]] = relationship(
        secondary="roles_profiles_m2m",
        back_populates="profiles_m2m"
    )
