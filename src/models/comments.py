from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.users import Base
from uuid import UUID
from sqlalchemy import ForeignKey
from src.models.posts import PostModel


class CommentModel(Base):
    __tablename__ = 'comment'

    id: Mapped[UUID] = mapped_column(primary_key=True)

    post_id: Mapped[UUID] = mapped_column(
        ForeignKey('posts.id'),
        ondelete="CASCADE",
        nullable=False
    )

    post: Mapped[PostModel] = relationship(
        back_populates="comments"
    )

    author_id: Mapped[UUID] = mapped_column()
    content: Mapped[str] = mapped_column(default="")
    is_edited: Mapped[bool] = mapped_column(default=False)


