from uuid import UUID
from pydantic import BaseModel

from schemas.orders import OrderCreate


class PostCreate(BaseModel):
    title: str
    content: str
    order: OrderCreate | None = None


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


