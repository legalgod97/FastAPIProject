from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.comments import CommentModel


roles_comments_m2m = sa.Table(
    "roles_comments_m2m",
    Base.metadata,
    sa.Column(
        "role_id",
        sa.ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "comment_id",
        sa.ForeignKey("comments.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    extend_existing=True,  # 👈 ключевой момент
)


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]

    main_comment: Mapped["CommentModel"] = relationship(
        "CommentModel",
        back_populates="role_o2o",
        foreign_keys="CommentModel.role_o2o_id",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )

    comments: Mapped[list["CommentModel"]] = relationship(
        "CommentModel",
        foreign_keys="CommentModel.role_o2m_id",
        back_populates="role_o2m",
    )

    shared_comments: Mapped[list["CommentModel"]] = relationship(
        secondary=roles_comments_m2m,
        back_populates="roles",
    )
