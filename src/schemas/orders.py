from uuid import UUID
from pydantic import BaseModel, field_validator

from src.exceptions.common import ValidationError
from src.schemas.posts import PostReadShort


class OrderCreate(BaseModel):
    price: int

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValidationError("Price")
        return v


class OrderUpdate(BaseModel):
    price: int | None = None


class OrderRead(BaseModel):
    id: UUID
    price: int
    post: PostReadShort | None = None

    model_config = {
        "from_attributes": True,
    }