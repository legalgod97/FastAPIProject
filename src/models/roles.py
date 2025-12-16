import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.users import Base
from uuid import UUID, uuid4
from models.comments import CommentModel


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
)


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]

    main_comment: Mapped["CommentModel"] = relationship(
        back_populates="role_o2o",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )

    comments: Mapped[list["CommentModel"]] = relationship(
        back_populates="role_o2m",
        cascade="all, delete-orphan",
    )

    shared_comments: Mapped[list["CommentModel"]] = relationship(
        secondary="roles_comments_m2m",
        back_populates="roles",
    )