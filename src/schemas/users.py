from uuid import UUID
from pydantic import BaseModel


class UserCreate(BaseModel):
    id: UUID | None = None
    name: str


class UserRead(BaseModel):
    id: UUID
    name: str

    model_config = {
        "from_attributes": True
    }


class UserUpdate(BaseModel):
    name: str | None = None