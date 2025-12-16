from uuid import UUID
from pydantic import BaseModel

from schemas.posts import PostRead


class OrderCreate(BaseModel):
    id: UUID | None = None
    price: int


class OrderUpdate(BaseModel):
    price: int | None = None


class OrderRead(BaseModel):
    id: UUID
    price: int
    post: PostRead | None = None

    model_config = {
        "from_attributes": True
    }