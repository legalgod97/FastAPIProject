from uuid import UUID
from pydantic import BaseModel


class CommentBase(BaseModel):
    post_id: UUID | None = None
    author_id: UUID | None = None
    content: str | None = None


class CommentCreate(CommentBase):
    post_id: UUID
    author_id: UUID
    content: str


class CommentUpdate(CommentBase):
    pass


class CommentOut(BaseModel):
    id: UUID
    post_id: UUID
    author_id: UUID
    content: str
    is_edited: bool

    class Config:
        from_attributes = True
