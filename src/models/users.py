import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeMeta, Mapped, declarative_base, mapped_column, relationship
from uuid import UUID, uuid4

from models.orders import OrderModel
from models.posts import PostModel
from models.roles import RoleModel
from src.models.profiles import ProfileModel
from sqlalchemy import ForeignKey


metadata = sa.MetaData()


class BaseServiceModel:
    """Базовый класс для таблиц сервиса."""

    @classmethod
    def on_conflict_constraint(cls) -> tuple | None:
        return None


Base: DeclarativeMeta = declarative_base(metadata=metadata, cls=BaseServiceModel)


class UserModel(Base):
    __tablename__ = 'user'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(sa.String())

    profile: Mapped[ProfileModel] = relationship(
        back_populates="user",
        uselist=False
    )

    role_name: Mapped[str] = mapped_column(
        ForeignKey('role.name'),
        unique=True,
        nullable=True
    )

    role: Mapped[RoleModel] = relationship(
        back_populates="user",
        uselist=False
    )

    posts: Mapped[list[PostModel]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    orders: Mapped[list[OrderModel]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )



