from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from infrastructure.db.models.users import UserModel
from infrastructure.db.models.users import Base
from sqlalchemy import ForeignKey
from datetime import datetime


class ProfileModel(Base):
    __tablename__ = 'profile'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"),
        unique=True
    )

    user: Mapped[UserModel] = relationship(back_populates="profile")
    full_name: Mapped[str] = mapped_column()
    avatar_url: Mapped[str] = mapped_column()
    bio: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    birth_date: Mapped[datetime] = mapped_column()
    gender: Mapped[str] = mapped_column()
    phone_number: Mapped[str] = mapped_column()
