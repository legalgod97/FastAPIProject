from uuid import UUID
from pydantic import BaseModel


class ProfileCreate(BaseModel):
    full_name: str
    bio: str
    role_id: UUID | None = None
    role_o2m_id: UUID | None = None


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
