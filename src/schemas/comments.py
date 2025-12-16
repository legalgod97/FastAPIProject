from uuid import UUID
from pydantic import BaseModel, field_validator, Field

from schemas.roles import RoleRead


class CommentBase(BaseModel):
    post_id: UUID | None = None
    author_id: UUID | None = None
    content: str | None = None


class CommentCreate(CommentBase):
    post_id: UUID
    author_id: UUID
    content: str


class CommentUpdate(CommentBase):
    content: str
    is_edited: bool

    @field_validator('is_edited', mode='before')
    def mark_is_edited(cls, v, info):
        if 'content' in info.data and info.data['content'] is not None:
            return True
        return v


class CommentOut(BaseModel):
    id: UUID
    post_id: UUID
    author_id: UUID
    content: str
    is_edited: bool

    class Config:
        from_attributes = True


class CommentRead(BaseModel):
    id: UUID
    content: str
    is_edited: bool
    role: RoleRead | None

    model_config = {
        "from_attributes": True
    }
