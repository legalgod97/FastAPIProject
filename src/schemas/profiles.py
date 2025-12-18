from uuid import UUID
from pydantic import BaseModel, field_validator

from exceptions.common import ValidationError


class ProfileCreate(BaseModel):
    full_name: str
    bio: str
    role_id: UUID | None = None
    role_o2m_id: UUID | None = None

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationError("Full name")
        return v


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    role_id: UUID | None = None
    role_o2m_id: UUID | None = None


class ProfileRead(BaseModel):
    id: UUID
    full_name: str
    bio: str
    owner_id: UUID | None
    role_id: UUID | None
    role_o2m_id: UUID | None

    class Config:
        from_attributes = True
