from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from sqlalchemy import ForeignKey
from models.users import Base
from models.roles import RoleModel


class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    content: Mapped[str] = mapped_column(default="")
    is_edited: Mapped[bool] = mapped_column(default=False)

    role_o2o_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        unique=True,
    )

    role_o2o: Mapped["RoleModel"] = relationship(
        back_populates="main_comment"
    )

    role_o2m_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE")
    )

    role_o2m: Mapped["RoleModel"] = relationship(
        back_populates="comments"
    )

    roles: Mapped[list["RoleModel"]] = relationship(
        secondary="roles_comments_m2m",
        back_populates="shared_comments",
    )
