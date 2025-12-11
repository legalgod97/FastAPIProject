from uuid import UUID
from pydantic import BaseModel

class OrderCreate(BaseModel):
    id: UUID | None = None
    price: int


class OrderUpdate(BaseModel):
    price: int | None = None


