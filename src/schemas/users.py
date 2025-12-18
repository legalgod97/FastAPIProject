from uuid import UUID
from pydantic import BaseModel, field_validator

from schemas.profiles import ProfileCreate


class UserCreate(BaseModel):
    name: str
    profile: ProfileCreate | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v


class UserRead(BaseModel):
    id: UUID
    name: str

    model_config = {
        "from_attributes": True
    }


class UserUpdate(BaseModel):
    name: str | None = None