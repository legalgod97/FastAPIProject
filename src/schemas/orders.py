from uuid import UUID
from pydantic import BaseModel, field_validator

from schemas.posts import PostRead, PostCreate


class OrderCreate(BaseModel):
    price: int
    post: PostCreate | None = None

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("price must be greater than 0")
        return v


class OrderUpdate(BaseModel):
    price: int | None = None


class OrderRead(BaseModel):
    id: UUID
    price: int
    post: PostRead | None = None

    model_config = {
        "from_attributes": True
    }