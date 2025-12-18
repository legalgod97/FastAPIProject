from uuid import UUID
from pydantic import BaseModel, field_validator

from exceptions.common import ValidationError
from schemas.orders import OrderCreate


class PostCreate(BaseModel):
    title: str
    content: str
    order: OrderCreate | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationError("Title")
        return v


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class PostRead(BaseModel):
    id: UUID
    title: str
    content: str

    model_config = {
        "from_attributes": True
    }


