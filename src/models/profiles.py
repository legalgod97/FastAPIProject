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
    full_name: Mapped[str]
    bio: Mapped[str]

    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    owner: Mapped["UserModel"] = relationship(
        back_populates="profiles"
    )

