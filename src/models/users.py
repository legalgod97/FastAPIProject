import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeMeta, Mapped, declarative_base, mapped_column, relationship
from uuid import UUID, uuid4
from models.profiles import ProfileModel


metadata = sa.MetaData()


class BaseServiceModel:
    """Базовый класс для таблиц сервиса."""

    @classmethod
    def on_conflict_constraint(cls) -> tuple | None:
        return None


Base: DeclarativeMeta = declarative_base(metadata=metadata, cls=BaseServiceModel)

user_profile = sa.Table(
    "user_profile",
    Base.metadata,
    sa.Column("user_id", sa.ForeignKey("user.id"), primary_key=True),
    sa.Column("profile_id", sa.ForeignKey("profile.id"), primary_key=True),
)


class UserModel(Base):
    __tablename__ = "user"

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


