from uuid import UUID
from pydantic import BaseModel, field_validator
from src.exceptions.common import ValidationError
from src.schemas.roles import RoleRead


class CommentCreate(BaseModel):
    content: str
    post_id: UUID
    author_id: UUID
    role_id: UUID

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationError("Comment content")
        return v


class CommentUpdate(BaseModel):
    content: str | None = None
    is_edited: bool | None = None

    @field_validator("is_edited", mode="before")
    @classmethod
    def mark_is_edited(cls, v, info):
        if info.data.get("content") is not None:
            return True
        return v

class CommentRead(BaseModel):
    id: UUID
    content: str
    is_edited: bool
    role: RoleRead | None = None

    model_config = {
        "from_attributes": True
    }