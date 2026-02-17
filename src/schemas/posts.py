from uuid import UUID
from pydantic import BaseModel, field_validator

from src.exceptions.common import ValidationError


class PostCreate(BaseModel):
    title: str
    content: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationError("Title")
        return v


class PostRead(BaseModel):
    id: UUID
    title: str
    content: str

    model_config = {
        "from_attributes": True,
    }

class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class PostReadShort(BaseModel):
    id: UUID
    title: str

    model_config = {
        "from_attributes": True,
    }