from uuid import UUID
from pydantic import BaseModel

from schemas.profiles import ProfileCreate


class UserCreate(BaseModel):
    name: str
    profile: ProfileCreate | None = None


class UserRead(BaseModel):
    id: UUID
    name: str

    model_config = {
        "from_attributes": True
    }


class UserUpdate(BaseModel):
    name: str | None = None